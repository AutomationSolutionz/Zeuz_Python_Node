from Framework.install_handler.utils import send_response
from .linux_utils import (
    detect_package_manager,
    check_all_packages_installed,
    install_packages,
)


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
    print("Checking AT-SPI development packages status...")

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
    if check_all_packages_installed(package_manager, packages):
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
    print("Installing AT-SPI development packages...")

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

        success, error_msg = install_packages(
            package_manager, packages, user_password, timeout=3600
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
