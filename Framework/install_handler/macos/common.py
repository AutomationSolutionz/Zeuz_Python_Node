import asyncio
import platform
import os
import shutil
import subprocess
from Framework.install_handler.utils import send_response


async def _send_status(category, status: str, comment: str):
    """Helper to send status responses."""
    await send_response(
        {
            "action": "status",
            "data": {
                "category": category,
                "name": "Xcode",
                "status": status,
                "comment": comment,
            },
        }
    )


async def xcode_check_status(category) -> bool:
    """Check if Xcode is installed and license is accepted."""
    print("[xcode] Checking status...")

    if platform.system().lower() != "darwin":
        await _send_status(
            category, "error", "Unsupported OS. Xcode is only available on macOS."
        )
        return False

    xcodebuild_path = shutil.which("xcodebuild")
    if not xcodebuild_path or not os.path.exists("/Applications/Xcode.app"):
        await _send_status(category, "not installed", "Xcode is not installed.")
        return False

    try:
        # Check version
        result = subprocess.run(
            [xcodebuild_path, "-version"], capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            await _send_status(
                category, "error", f"xcodebuild error: {result.stderr.strip()}"
            )
            return False

        version = result.stdout.splitlines()[0].strip() if result.stdout else "unknown"

        # Check license
        license_result = subprocess.run(
            [xcodebuild_path, "-checkFirstLaunchStatus"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        if license_result.returncode == 0:
            await _send_status(category, "installed", f"{version}")
            return True
        else:
            await _send_status(
                category,
                "not installed",
                f"{version} installed but license not accepted.",
            )
            return False

    except subprocess.TimeoutExpired:
        await _send_status(category, "error", "xcodebuild timed out.")
        return False
    except Exception as e:
        await _send_status(category, "error", f"Error checking Xcode: {e}")
        return False


async def _accept_license(category, user_password: str) -> bool:
    """Attempt to accept Xcode license using sudo."""
    xcodebuild_path = shutil.which("xcodebuild") or "xcodebuild"

    if not user_password:
        await _send_status(
            category, "error", "Password required to accept Xcode license."
        )
        return False

    try:
        result = subprocess.run(
            ["sudo", "-S", xcodebuild_path, "-license", "accept"],
            input=user_password + "\n",
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            await _send_status(
                category, "installed", "Xcode license accepted successfully."
            )
            return True
        else:
            await _send_status(
                category, "error", f"Failed to accept license: {result.stderr.strip()}"
            )
            return False
    except Exception as e:
        await _send_status(category, "error", f"Error accepting license: {e}")
        return False


async def xcode_install(category, user_password: str = "") -> bool:
    """Install Xcode via App Store and accept license."""
    print("[xcode] Installing...")

    if platform.system().lower() != "darwin":
        await _send_status(
            category, "error", "Unsupported OS. Xcode is only available on macOS."
        )
        return False

    if await xcode_check_status(category):
        return True

    # Open App Store
    await _send_status(
        category, "installing", "Opening App Store. Please install Xcode and wait..."
    )
    try:
        subprocess.run(
            ["open", "itms-apps://itunes.apple.com/app/id497799835"], timeout=10
        )
    except Exception:
        pass

    # Poll for installation (2 hours timeout)
    timeout_seconds = 2 * 60 * 60
    interval = 10
    elapsed = 0

    while elapsed < timeout_seconds:
        await asyncio.sleep(interval)
        elapsed += interval

        # Check if Xcode app exists
        xcodebuild_path = shutil.which("xcodebuild")
        if os.path.exists("/Applications/Xcode.app") and xcodebuild_path:
            # Check license status
            try:
                license_result = subprocess.run(
                    [xcodebuild_path, "-checkFirstLaunchStatus"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )

                if license_result.returncode == 0:
                    await _send_status(
                        category, "installed", "Xcode installed successfully."
                    )
                    return True
                else:
                    # License not accepted, attempt to accept
                    return await _accept_license(category, user_password)
            except Exception:
                # Try to accept license anyway
                return await _accept_license(category, user_password)

    await _send_status(category, "error", "Timed out waiting for Xcode installation.")
    return False
