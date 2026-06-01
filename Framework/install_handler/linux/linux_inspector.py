import os
import re
import subprocess
import sys
import asyncio
from Framework.install_handler.install_log_config import get_logger
from Framework.install_handler.utils import send_response
from .linux_utils import (
    detect_package_manager,
    check_all_packages_installed,
    install_packages,
)

logger = get_logger()

CATEGORY = "Linux"
NAME = "Linux Inspector"

PACKAGES = {
    "apt": [
        "build-essential",
        "cmake",
        "pkg-config",
        "libgirepository1.0-dev",
        "libcairo2-dev",
        "xdotool",
        "x11-apps",
        "imagemagick",
        "wmctrl",
    ],
    "dnf": [
        "cmake",
        "pkgconf-pkg-config",
        "gobject-introspection-devel",
        "cairo-devel",
        "xdotool",
        "ImageMagick",
        "wmctrl",
        "python3-devel",
        "cairo-gobject-devel",
    ],
    "pacman": [
        "gcc",
        "meson",
        "cmake",
        "pkgconf",
        "cairo",
        "xdotool",
        "gobject-introspection",
        "imagemagick",
        "wmctrl",
    ],
}

# Final packages installed in the AlmaLinux/RHEL 9 sequence (used for status check)
ALMA_RHEL9_CHECK_PACKAGES = [
    "xdotool",
    "ImageMagick",
    "wmctrl",
    "python3-devel",
]

PIP_PACKAGES = [
    "python3-pyatspi==1.19.0",
    "pygobject==3.50.1",
    "python-xlib==0.33",
]

ACCESSIBILITY_VARS = [
    "export NO_AT_BRIDGE=0",
    "export GTK_MODULES=gail:atk-bridge",
    "export ACCESSIBILITY_ENABLED=1",
]
ACCESSIBILITY_MARKER = "# zeuz-accessibility"


def _is_alma_rhel9() -> bool:
    try:
        with open("/etc/os-release") as f:
            content = f.read()
        return bool(re.search(r"AlmaLinux.*9|Red Hat.*9|Rocky.*9", content, re.IGNORECASE))
    except Exception:
        return False


def _check_pip_packages_installed() -> bool:
    for pkg in PIP_PACKAGES:
        name = pkg.split("==")[0]
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", name],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return False
    return True


def _install_pip_packages() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install"] + PIP_PACKAGES,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode == 0:
            return True, ""
        return False, result.stderr
    except subprocess.TimeoutExpired:
        return False, "pip install timed out"
    except Exception as e:
        return False, str(e)


def _add_accessibility_env_vars():
    for rc_file in [
        os.path.expanduser("~/.bashrc"),
        os.path.expanduser("~/.zshrc"),
    ]:
        if not os.path.isfile(rc_file):
            continue
        try:
            with open(rc_file) as f:
                content = f.read()
            if ACCESSIBILITY_MARKER in content:
                continue
            with open(rc_file, "a") as f:
                f.write(f"\n{ACCESSIBILITY_MARKER}\n")
                for line in ACCESSIBILITY_VARS:
                    f.write(f"{line}\n")
        except Exception:
            pass


def _enable_gnome_accessibility():
    try:
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface", "toolkit-accessibility", "true"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        pass


def _run_sudo_cmd(cmd: list[str], user_password: str, timeout: int = 3600) -> tuple[bool, str]:
    """Run a sudo command, optionally passing password via stdin."""
    if user_password:
        full_cmd = ["sudo", "-S"] + cmd
        process = subprocess.Popen(
            full_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _, stderr = process.communicate(input=f"{user_password}\n", timeout=timeout)
        return process.returncode == 0, stderr
    else:
        full_cmd = ["sudo"] + cmd
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stderr


def _install_alma_rhel9(user_password: str) -> tuple[bool, str]:
    steps = [
        (["dnf", "groupinstall", "Development Tools", "-y"], 600),
        (["dnf", "install", "-y", "cairo-devel", "pkg-config"], 300),
        (["dnf", "config-manager", "--set-enabled", "crb"], 60),
        (["dnf", "install", "-y", "gobject-introspection-devel", "at-spi2-core-devel", "cairo-gobject-devel"], 300),
        (["dnf", "install", "-y", "epel-release"], 120),
        (["dnf", "install", "-y", "xwd", "xdotool", "ImageMagick", "wmctrl", "python3-devel"], 300),
    ]
    for cmd, timeout in steps:
        success, err = _run_sudo_cmd(cmd, user_password, timeout=timeout)
        if not success:
            return False, f"Step '{' '.join(cmd)}' failed: {err}"
    return True, ""


async def check_status():
    """Check if Linux Inspector dependencies are installed."""
    logger.info("Checking Linux Inspector status...")

    session_type = os.environ.get("XDG_SESSION_TYPE", "unknown")
    if session_type != "x11":
        await send_response({
            "action": "status",
            "data": {
                "category": CATEGORY,
                "name": NAME,
                "status": "error",
                "comment": f"Only X11 is supported. Current session type: {session_type}.",
            },
        })
        return False

    package_manager, _ = detect_package_manager()
    if not package_manager:
        await send_response({
            "action": "status",
            "data": {
                "category": CATEGORY,
                "name": NAME,
                "status": "error",
                "comment": "Unsupported package manager. Only apt, dnf, and pacman are supported.",
            },
        })
        return False

    if package_manager == "dnf" and _is_alma_rhel9():
        sys_ok = await asyncio.to_thread(check_all_packages_installed, package_manager, ALMA_RHEL9_CHECK_PACKAGES)
    else:
        sys_ok = await asyncio.to_thread(check_all_packages_installed, package_manager, PACKAGES[package_manager])

    pip_ok = _check_pip_packages_installed()

    if sys_ok and pip_ok:
        await send_response({
            "action": "status",
            "data": {
                "category": CATEGORY,
                "name": NAME,
                "status": "installed",
                "comment": "Linux Inspector dependencies are installed.",
            },
        })
        return True
    else:
        missing = []
        if not sys_ok:
            missing.append("system packages")
        if not pip_ok:
            missing.append("Python packages")
        await send_response({
            "action": "status",
            "data": {
                "category": CATEGORY,
                "name": NAME,
                "status": "not installed",
                "comment": f"Missing: {', '.join(missing)}. Use Install to set up.",
            },
        })
        return False


async def install(user_password: str = ""):
    """Install Linux Inspector dependencies."""
    logger.info("Installing Linux Inspector dependencies...")

    session_type = os.environ.get("XDG_SESSION_TYPE", "unknown")
    if session_type != "x11":
        await send_response({
            "action": "status",
            "data": {
                "category": CATEGORY,
                "name": NAME,
                "status": "error",
                "comment": f"Only X11 is supported. Current session type: {session_type}.",
            },
        })
        return False

    already_installed = await check_status()
    if already_installed:
        return True

    package_manager, _ = detect_package_manager()
    if not package_manager:
        await send_response({
            "action": "status",
            "data": {
                "category": CATEGORY,
                "name": NAME,
                "status": "error",
                "comment": "Unsupported package manager. Only apt, dnf, and pacman are supported.",
            },
        })
        return False

    await send_response({
        "action": "status",
        "data": {
            "category": CATEGORY,
            "name": NAME,
            "status": "installing",
            "comment": "Installing system packages, please wait...",
        },
    })

    # Install system packages
    if package_manager == "dnf" and _is_alma_rhel9():
        success, error_msg = await asyncio.to_thread(_install_alma_rhel9, user_password)
    else:
        success, error_msg = await asyncio.to_thread(
            install_packages, package_manager, PACKAGES[package_manager], user_password
        )

    if not success:
        await send_response({
            "action": "status",
            "data": {
                "category": CATEGORY,
                "name": NAME,
                "status": "error",
                "comment": f"System package installation failed: {error_msg}",
            },
        })
        return False

    # Install Python packages
    await send_response({
        "action": "status",
        "data": {
            "category": CATEGORY,
            "name": NAME,
            "status": "installing",
            "comment": "Installing Python packages, please wait...",
        },
    })

    pip_success, pip_error = await asyncio.to_thread(_install_pip_packages)
    if not pip_success:
        await send_response({
            "action": "status",
            "data": {
                "category": CATEGORY,
                "name": NAME,
                "status": "error",
                "comment": f"Python package installation failed: {pip_error}",
            },
        })
        return False

    # Set up accessibility env vars and GNOME setting
    await asyncio.to_thread(_add_accessibility_env_vars)
    await asyncio.to_thread(_enable_gnome_accessibility)

    await send_response({
        "action": "status",
        "data": {
            "category": CATEGORY,
            "name": NAME,
            "status": "installed",
            "comment": "Linux Inspector dependencies installed successfully.",
        },
    })
    return True
