import platform
import os
import shutil
import subprocess
from pathlib import Path
from Framework.install_handler.utils import send_response


async def _send_status(status: str, comment: str):
    """Helper to send status responses."""
    await send_response(
        {
            "action": "status",
            "data": {
                "category": "iOS",
                "name": "WebDriver",
                "status": status,
                "comment": comment,
            },
        }
    )


def _get_webdriver_path() -> Path:
    """Get the path where WebDriverAgent should be installed."""
    home = Path.home()
    return home / ".zeuz" / "WebDriverAgent"


async def _check_xcode_installed() -> bool:
    """Check if Xcode is installed."""
    if not os.path.exists("/Applications/Xcode.app"):
        return False
    
    xcodebuild_path = shutil.which("xcodebuild")
    if not xcodebuild_path:
        return False
    
    try:
        result = subprocess.run(
            [xcodebuild_path, "-version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0
    except Exception:
        return False


async def _get_available_simulator() -> str | None:
    """Get the first available iOS simulator device name."""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "available", "iOS"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        if result.returncode != 0:
            return None
        
        # Parse output to find first iPhone or iPad simulator
        for line in result.stdout.splitlines():
            line = line.strip()
            # Look for device lines like "iPhone 16 Pro (UUID) (Shutdown)"
            if "iPhone" in line  and "(" in line:
                # Extract device name (everything before first parenthesis)
                device_name = line.split("(")[0].strip()
                if device_name:
                    return device_name
        
        return None
    except Exception:
        return None


async def check_status() -> bool:
    """Check if WebDriverAgent is installed and built."""
    print("[webdriver] Checking status...")

    if platform.system().lower() != "darwin":
        await _send_status(
            "error", "Unsupported OS. WebDriverAgent is only available on macOS."
        )
        return False

    # Check if Xcode is installed
    if not await _check_xcode_installed():
        await _send_status(
            "not installed", "Xcode must be installed before using WebDriverAgent."
        )
        return False

    webdriver_path = _get_webdriver_path()
    project_path = webdriver_path / "WebDriverAgent.xcodeproj"

    # Check if WebDriverAgent is cloned
    if not project_path.exists():
        await _send_status(
            "not installed", "WebDriverAgent repository is not cloned."
        )
        return False

    # Check if the project has been built
    # Look for derived data or built products
    try:
        # Check if we can read the project
        result = subprocess.run(
            ["xcodebuild", "-project", str(project_path), "-list"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(webdriver_path),
        )
        
        if result.returncode != 0:
            await _send_status(
                "not installed", f"WebDriverAgent project is invalid: {result.stderr.strip()}"
            )
            return False

        # Check if WebDriverAgentRunner scheme exists
        if "WebDriverAgentRunner" in result.stdout:
            await _send_status(
                "installed", f"WebDriverAgent is installed at {webdriver_path}"
            )
            return True
        else:
            await _send_status(
                "not installed", "WebDriverAgentRunner scheme not found in project."
            )
            return False

    except subprocess.TimeoutExpired:
        await _send_status("error", "xcodebuild command timed out.")
        return False
    except Exception as e:
        await _send_status("error", f"Error checking WebDriverAgent: {e}")
        return False


async def _clone_repository(webdriver_path: Path) -> bool:
    """Clone the WebDriverAgent repository."""
    try:
        # Remove existing directory if it exists but is incomplete
        if webdriver_path.exists():
            await _send_status(
                "installing", "Removing incomplete WebDriverAgent installation..."
            )
            shutil.rmtree(webdriver_path)

        # Create parent directory
        webdriver_path.parent.mkdir(parents=True, exist_ok=True)

        await _send_status(
            "installing", "Cloning WebDriverAgent repository, please wait..."
        )

        # Clone the repository
        result = subprocess.run(
            [
                "git", "clone",
                "--depth", "1",  # Shallow clone for faster download
                "https://github.com/appium/WebDriverAgent.git",
                str(webdriver_path)
            ],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes timeout
        )

        if result.returncode != 0:
            await _send_status(
                "error", f"Failed to clone repository: {result.stderr.strip()}"
            )
            return False

        return True

    except subprocess.TimeoutExpired:
        await _send_status("error", "Git clone timed out.")
        return False
    except Exception as e:
        await _send_status("error", f"Error cloning repository: {e}")
        return False


async def _bootstrap_webdriver(webdriver_path: Path) -> bool:
    """Run the bootstrap script if it exists."""
    bootstrap_script = webdriver_path / "Scripts" / "bootstrap.sh"
    
    if not bootstrap_script.exists():
        # Try alternative path
        bootstrap_script = webdriver_path / "bootstrap.sh"
    
    if bootstrap_script.exists():
        try:
            await _send_status(
                "installing", "Running WebDriverAgent bootstrap script..."
            )
            
            result = subprocess.run(
                ["bash", str(bootstrap_script)],
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(webdriver_path),
            )
            
            if result.returncode != 0:
                # Non-fatal, just log it
                print(f"Bootstrap warning: {result.stderr.strip()}")
            
            return True
        except Exception as e:
            # Non-fatal
            print(f"Bootstrap warning: {e}")
            return True
    
    return True


async def _build_webdriver(webdriver_path: Path) -> bool:
    """Build WebDriverAgent project."""
    try:
        project_path = webdriver_path / "WebDriverAgent.xcodeproj"
        
        # Get available simulator
        simulator_name = await _get_available_simulator()
        if not simulator_name:
            await _send_status(
                "error", "No iOS Simulator found. Please install iOS Simulator first."
            )
            return False

        await _send_status(
            "installing", f"Building WebDriverAgent for {simulator_name}, please wait (this may take several minutes)..."
        )

        # Build the project
        destination = f"platform=iOS Simulator,name={simulator_name}"
        
        result = subprocess.run(
            [
                "xcodebuild",
                "-project", str(project_path),
                "-scheme", "WebDriverAgentRunner",
                "-destination", destination,
                "-allowProvisioningUpdates",
                "build-for-testing",
            ],
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minutes timeout for build
            cwd=str(webdriver_path),
        )

        if result.returncode != 0:
            # Check if it's a signing error (common issue)
            if "code signing" in result.stderr.lower() or "signing" in result.stderr.lower():
                await _send_status(
                    "error", 
                    "Code signing error. Please open Xcode, go to WebDriverAgent project, "
                    "and configure signing in the target settings."
                )
            else:
                await _send_status(
                    "error", f"Build failed: {result.stderr.strip()[-500:]}"  # Last 500 chars
                )
            return False

        await _send_status(
            "installed", f"WebDriverAgent built successfully for {simulator_name}"
        )
        return True

    except subprocess.TimeoutExpired:
        await _send_status("error", "Build timed out (exceeded 30 minutes).")
        return False
    except Exception as e:
        await _send_status("error", f"Error building WebDriverAgent: {e}")
        return False


async def install(user_password: str = "") -> bool:
    """Install WebDriverAgent by cloning and building the project."""
    print("[webdriver] Installing...")

    if platform.system().lower() != "darwin":
        await _send_status(
            "error", "Unsupported OS. WebDriverAgent is only available on macOS."
        )
        return False

    # Check if already installed
    if await check_status():
        return True

    # Ensure Xcode is installed
    if not await _check_xcode_installed():
        await _send_status(
            "error", "Xcode must be installed first. Please install Xcode from the App Store."
        )
        return False

    # Check if git is available
    if not shutil.which("git"):
        await _send_status(
            "error", "Git is not installed. Please install git first."
        )
        return False

    webdriver_path = _get_webdriver_path()

    # Clone repository
    if not await _clone_repository(webdriver_path):
        return False

    # Bootstrap (optional step)
    await _bootstrap_webdriver(webdriver_path)

    # Build the project
    if not await _build_webdriver(webdriver_path):
        return False

    # Final verification
    if await check_status():
        await _send_status(
            "installed", f"WebDriverAgent is ready to use at {webdriver_path}"
        )
        return True
    else:
        await _send_status(
            "error", "Installation completed but verification failed."
        )
        return False
