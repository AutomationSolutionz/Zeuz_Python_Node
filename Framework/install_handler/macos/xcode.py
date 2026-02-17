from .common import xcode_check_status, xcode_install


async def check_status() -> bool:
    """Check if Xcode is installed and license is accepted."""
    print("[xcode] Checking status...")

    return await xcode_check_status("MacOS")



async def install(user_password: str = "") -> bool:
    """Install Xcode via App Store and accept license."""
    print("[xcode] Installing...")

    return await xcode_install("MacOS", user_password)
