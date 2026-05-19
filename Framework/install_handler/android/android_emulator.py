import platform

from Framework.install_handler.install_log_config import get_logger
from . import emulator as emulator_macos
from . import emulator_windows_linux

logger = get_logger()

def _is_darwin() -> bool:
    return platform.system().lower() == "darwin"


async def check_emulator_list():
    """
    OS router for AndroidEmulator system images services.
    - macOS: uses `emulator.py`
    - Windows/Linux: uses `emulator_windows_linux.py`
    """
    system = platform.system().lower()
    if system == "darwin":
        logger.debug("[android_emulator] Routing to macOS emulator module")
        return await emulator_macos.check_emulator_list()

    logger.debug("[android_emulator] Routing to Windows/Linux emulator module")
    return await emulator_windows_linux.check_emulator_list()


async def android_emulator_install():
    """
    OS router for AndroidEmulator installation.
    - macOS: uses `emulator.py`
    - Windows/Linux: uses `emulator_windows_linux.py`
    """
    system = platform.system().lower()
    if system == "darwin":
        logger.debug("[android_emulator] Routing to macOS emulator module")
        return await emulator_macos.android_emulator_install()

    logger.debug("[android_emulator] Routing to Windows/Linux emulator module")
    return await emulator_windows_linux.android_emulator_install()


async def create_avd_from_system_image(device_param: str) -> bool:
    """
    Create an AVD from a chosen system-image device param.
    Routes to the correct platform implementation dynamically.
    """
    if _is_darwin():
        logger.debug("[android_emulator] Routing create_avd to macOS module")
        return await emulator_macos.create_avd_from_system_image(device_param)
    logger.debug("[android_emulator] Routing create_avd to Windows/Linux module")
    return await emulator_windows_linux.create_avd_from_system_image(device_param)


async def get_filtered_avd_services():
    """
    Return filtered AVD services to display on the installer UI.
    Routes to the correct platform implementation dynamically.
    """
    if _is_darwin():
        logger.debug("[android_emulator] Routing get_filtered_avd_services to macOS module")
        return await emulator_macos.get_filtered_avd_services()
    logger.debug("[android_emulator] Routing get_filtered_avd_services to Windows/Linux module")
    return await emulator_windows_linux.get_filtered_avd_services()


async def launch_avd(avd_name: str) -> bool:
    """
    Launch an existing AVD.
    Routes to the correct platform implementation dynamically.
    """
    if _is_darwin():
        logger.debug("[android_emulator] Routing launch_avd to macOS module")
        return await emulator_macos.launch_avd(avd_name)
    logger.debug("[android_emulator] Routing launch_avd to Windows/Linux module")
    return await emulator_windows_linux.launch_avd(avd_name)


