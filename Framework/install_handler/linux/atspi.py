import asyncio
import os
from Framework.install_handler.install_log_config import get_logger
from Framework.install_handler.utils import send_response
from .linux_utils import (
    detect_package_manager,
    check_all_packages_installed,
    install_packages,
)

logger = get_logger()


# Package definitions for different package managers
PACKAGES = {
    "apt": [
        "build-essential",
        "cmake",
        "pkg-config",
        "libgirepository1.0-dev",
        "libcairo2-dev",
        "xdotool",
    ],
    "dnf": [
        "cmake",
        "pkgconf-pkg-config",
        "gobject-introspection-devel",
        "cairo-devel",
        "python3-devel",
        "cairo-gobject-devel",
        "xdotool",
    ],
    "pacman": [
        "gcc",
        "meson",
        "cmake",
        "pkgconf",
        "cairo",
        "xdotool",
        "gobject-introspection",
    ],
}


async def check_status():
    """Checks if AT-SPI development packages are installed."""
    logger.info("Checking AT-SPI development packages status...")

    # Check if session type is X11
    session_type = os.environ.get("XDG_SESSION_TYPE", "unknown")
    if session_type != "x11":
        await send_response(
            {
                "action": "status",
                "data": {
                    "category": "Linux",
                    "name": "AT-SPI Packages",
                    "status": "error",
                    "comment": f"Only X11 is supported. Current session type: {session_type}.",
                },
            }
        )
        return False

    package_manager, _ = detect_package_manager()

    if not package_manager:
        await send_response(
            {
                "action": "status",
                "data": {
                    "category": "Linux",
                    "name": "AT-SPI Packages",
                    "status": "error",
                    "comment": "Unsupported package manager. Only apt, dnf, and pacman are supported.",
                },
            }
        )
        return False

    packages = PACKAGES.get(package_manager, [])
    if await asyncio.to_thread(check_all_packages_installed, package_manager, packages):
        await send_response(
            {
                "action": "status",
                "data": {
                    "category": "Linux",
                    "name": "AT-SPI Packages",
                    "status": "installed",
                    "comment": "AT-SPI development packages are installed.",
                },
            }
        )
        return True
    else:
        await send_response(
            {
                "action": "status",
                "data": {
                    "category": "Linux",
                    "name": "AT-SPI Packages",
                    "status": "not installed",
                    "comment": f"Install AT-SPI packages using {package_manager}.",
                },
            }
        )
        return False


async def install(user_password: str = ""):
    """Install AT-SPI development packages using the system package manager."""
    logger.info("Installing AT-SPI development packages...")

    # Check if session type is X11
    session_type = os.environ.get("XDG_SESSION_TYPE", "unknown")
    if session_type != "x11":
        await send_response(
            {
                "action": "status",
                "data": {
                    "category": "Linux",
                    "name": "AT-SPI Packages",
                    "status": "error",
                    "comment": f"Only X11 is supported. Current session type: {session_type}.",
                },
            }
        )
        return False

    is_already_installed = await check_status()

    if not is_already_installed:
        package_manager, _ = detect_package_manager()

        if not package_manager:
            await send_response(
                {
                    "action": "status",
                    "data": {
                        "category": "Linux",
                        "name": "AT-SPI Packages",
                        "status": "error",
                        "comment": "Unsupported package manager. Only apt, dnf, and pacman are supported.",
                    },
                }
            )
            return False

        packages = PACKAGES.get(package_manager, [])
        await send_response(
            {
                "action": "status",
                "data": {
                    "category": "Linux",
                    "name": "AT-SPI Packages",
                    "status": "installing",
                    "comment": f"Installing packages using {package_manager}, please wait...",
                },
            }
        )

        success, error_msg = await asyncio.to_thread(
            install_packages, package_manager, packages, user_password, 3600
        )

        if success:
            await send_response(
                {
                    "action": "status",
                    "data": {
                        "category": "Linux",
                        "name": "AT-SPI Packages",
                        "status": "installed",
                        "comment": "AT-SPI packages have been installed successfully.",
                    },
                }
            )
            return True
        else:
            await send_response(
                {
                    "action": "status",
                    "data": {
                        "category": "Linux",
                        "name": "AT-SPI Packages",
                        "status": "error",
                        "comment": f"Installation failed. Error: {error_msg}",
                    },
                }
            )
            return False
    else:
        return True
