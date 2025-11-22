import asyncio
from Framework.Built_In_Automation.Web.Selenium.utils import ChromeForTesting
from Framework.install_handler.utils import send_response


async def check_status() -> bool:
    """Check if Chrome for Testing is installed."""
    print("[installer][web-chrome_for_testing] Checking status...")
    
    try:
        cft = ChromeForTesting()
        
        # Get the latest version
        latest_version = cft.get_latest_version(channel="Stable", force_check=False)
        
        if not latest_version:
            print("[installer][web-chrome_for_testing] Not installed (no version available)")
            await send_response({
                "action": "status",
                "data": {
                    "category": "Web",
                    "name": "Chrome For Testing",
                    "status": "not installed",
                    "comment": "Install Chrome for Testing to use it.",
                }
            })
            return False
        
        # Check if the latest version is installed
        is_installed = cft.is_version_installed(latest_version)
        
        if is_installed:
            print(f"[installer][web-chrome_for_testing] Already installed (version: {latest_version})")
            await send_response({
                "action": "status",
                "data": {
                    "category": "Web",
                    "name": "Chrome For Testing",
                    "status": "installed",
                    "comment": f"Chrome for Testing is installed (version: {latest_version})",
                }
            })
            return True
        else:
            print("[installer][web-chrome_for_testing] Not installed")
            await send_response({
                "action": "status",
                "data": {
                    "category": "Web",
                    "name": "Chrome For Testing",
                    "status": "not installed",
                    "comment": "Chrome for Testing is not installed. Install it to use it.",
                }
            })
            return False
    except Exception as e:
        print(f"[installer][web-chrome_for_testing] Error checking status: {e}")
        await send_response({
            "action": "status",
            "data": {
                "category": "Web",
                "name": "Chrome For Testing",
                "status": "not installed",
                "comment": "Unable to check Chrome for Testing status.",
            }
        })
        return False


async def install() -> bool:
    """Install Chrome for Testing."""
    print("[installer][web-chrome_for_testing] Installing...")
    
    # Check if already installed
    if await check_status():
        print("[installer][web-chrome_for_testing] Chrome for Testing is already installed")
        return True
    
    try:
        cft = ChromeForTesting()
        
        # Send initial status update
        await send_response({
            "action": "status",
            "data": {
                "category": "Web",
                "name": "ChromeForTesting",
                "status": "installing",
                "comment": "Download started. Check the terminal on which ZeuZ Node is open for updates",
            }
        })
        
        # Wrap synchronous setup_chrome_for_testing in executor to avoid blocking event loop
        loop = asyncio.get_event_loop()
        chrome_bin, driver_bin = await loop.run_in_executor(
            None,
            lambda: cft.setup_chrome_for_testing(version=None, channel="Stable")
        )
        
        if chrome_bin and driver_bin:
            print("[installer][web-chrome_for_testing] Chrome for Testing installation successful")
            await send_response({
                "action": "status",
                "data": {
                    "category": "Web",
                    "name": "ChromeForTesting",
                    "status": "installed",
                    "comment": "Chrome for Testing is installed",
                }
            })
            return True
        else:
            print("[installer][web-chrome_for_testing] Chrome for Testing installation failed")
            await send_response({
                "action": "status",
                "data": {
                    "category": "Web",
                    "name": "ChromeForTesting",
                    "status": "not installed",
                    "comment": "Failed to install Chrome for Testing",
                }
            })
            return False
    except FileNotFoundError as e:
        print(f"[installer][web-chrome_for_testing] Error installing: {e}")
        await send_response({
            "action": "status",
            "data": {
                "category": "Web",
                "name": "ChromeForTesting",
                "status": "not installed",
                "comment": f"Failed to install Chrome for Testing: Required binaries not found",
            }
        })
        return False
    except Exception as e:
        print(f"[installer][web-chrome_for_testing] Error installing: {e}")
        await send_response({
            "action": "status",
            "data": {
                "category": "Web",
                "name": "ChromeForTesting",
                "status": "not installed",
                "comment": f"Failed to install Chrome for Testing: {str(e)}",
            }
        })
        return False

