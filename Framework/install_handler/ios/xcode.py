from Framework.install_handler.install_log_config import get_logger
from Framework.install_handler.macos.common import xcode_check_status, xcode_install

logger = get_logger()


async def check_status() -> bool:
    """Check if Xcode is installed and license is accepted."""
    logger.info("[xcode] Checking status...")

    return await xcode_check_status("iOS")


async def install(user_password: str = "") -> bool:
    """Install Xcode via App Store and accept license."""
    logger.info("[xcode] Installing...")

    return await xcode_install("iOS", user_password)
