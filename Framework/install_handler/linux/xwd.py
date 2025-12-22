import os
from Framework.install_handler.utils import send_response
from .linux_utils import (
    detect_package_manager,
    check_all_packages_installed,
    install_packages,
)


# Package definitions for different package managers
PACKAGES = {
    "apt": [
        "x11-apps",  # provides xwd
        "imagemagick",  # provides convert, import
        "wmctrl",
    ],
    "dnf": [
        "xorg-x11-utils",  # provides xwd on some distros
        "ImageMagick",
        "wmctrl",
    ],
    "pacman": [
        "imagemagick",
        "wmctrl",
    ],
}


async def check_status():
    """Checks if Screen Capture Utilities are installed."""

    # Check if session type is X11
    session_type = os.environ.get("XDG_SESSION_TYPE", "unknown")
    if session_type != "x11":
        await send_response(
            {
                "action": "status",
                "data": {
                    "category": "Linux",
                    "name": "Screen Capture Utilities",
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
                    "name": "Screen Capture Utilities",
                    "status": "error",
                    "comment": "Unsupported package manager. Only apt, dnf, and pacman are supported.",
                },
            }
        )
        return False

    packages = PACKAGES.get(package_manager, [])
    if check_all_packages_installed(package_manager, packages):
        await send_response(
            {
                "action": "status",
                "data": {
                    "category": "Linux",
                    "name": "Screen Capture Utilities",
                    "status": "installed",
                    "comment": "Screen Capture Utilities are installed.",
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
                    "name": "Screen Capture Utilities",
                    "status": "not installed",
                    "comment": f"Install Screen Capture Utilities using {package_manager}.",
                },
            }
        )
        return False


async def install(user_password: str = ""):
    """Install Screen Capture Utilities using the system package manager."""

    # Check if session type is X11
    session_type = os.environ.get("XDG_SESSION_TYPE", "unknown")
    if session_type != "x11":
        await send_response(
            {
                "action": "status",
                "data": {
                    "category": "Linux",
                    "name": "Screen Capture Utilities",
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
                        "name": "Screen Capture Utilities",
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
                    "name": "Screen Capture Utilities",
                    "status": "installing",
                    "comment": f"Installing packages using {package_manager}, please wait...",
                },
            }
        )

        success, error_msg = install_packages(
            package_manager, packages, user_password, timeout=300
        )

        if success:
            await send_response(
                {
                    "action": "status",
                    "data": {
                        "category": "Linux",
                        "name": "Screen Capture Utilities",
                        "status": "installed",
                        "comment": "Screen Capture Utilities have been installed successfully.",
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
                        "name": "Screen Capture Utilities",
                        "status": "error",
                        "comment": f"Installation failed. Error: {error_msg}",
                    },
                }
            )
            return False
    else:
        return True
