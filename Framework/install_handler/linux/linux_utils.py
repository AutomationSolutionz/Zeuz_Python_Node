"""Shared utilities for Linux package management."""

import subprocess
import shutil


def detect_package_manager():
    """Detect the available package manager on the system.

    Returns:
        tuple: (package_manager_name, None) where package_manager_name is one of "apt", "dnf", "pacman", or None
    """
    if shutil.which("apt-get"):
        return "apt", None
    elif shutil.which("dnf"):
        return "dnf", None
    elif shutil.which("pacman"):
        return "pacman", None
    else:
        return None, None


def check_package_installed(package_manager, package):
    """Check if a package is installed using the appropriate package manager.

    Args:
        package_manager: One of "apt", "dnf", or "pacman"
        package: Package name to check

    Returns:
        bool: True if package is installed, False otherwise
    """
    try:
        if package_manager == "apt":
            result = subprocess.run(
                ["dpkg", "-s", package], capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0
        elif package_manager == "dnf":
            result = subprocess.run(
                ["rpm", "-q", package], capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0
        elif package_manager == "pacman":
            result = subprocess.run(
                ["pacman", "-Q", package], capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0
    except Exception:
        pass
    return False


def check_all_packages_installed(package_manager, packages):
    """Check if all packages in the list are installed.

    Args:
        package_manager: One of "apt", "dnf", or "pacman"
        packages: List of package names to check

    Returns:
        bool: True if all packages are installed, False otherwise
    """
    for package in packages:
        if not check_package_installed(package_manager, package):
            return False
    return True


def install_packages(package_manager, packages, user_password="", timeout=3600):
    """Install packages using the system package manager.

    Args:
        package_manager: One of "apt", "dnf", or "pacman"
        packages: List of package names to install
        user_password: Optional sudo password for authentication
        timeout: Timeout in seconds for the installation (default: 3600 = 1 hour)

    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        # Build the install command based on package manager
        if package_manager == "apt":
            if user_password:
                cmd = ["sudo", "-S", "apt-get", "install", "-y"] + packages
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                _, stderr = process.communicate(
                    input=f"{user_password}\n", timeout=timeout
                )
                success = process.returncode == 0
            else:
                cmd = ["sudo", "apt-get", "install", "-y"] + packages
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=timeout
                )
                success = result.returncode == 0
                stderr = result.stderr

        elif package_manager == "dnf":
            if user_password:
                cmd = ["sudo", "-S", "dnf", "install", "-y"] + packages
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                _, stderr = process.communicate(
                    input=f"{user_password}\n", timeout=timeout
                )
                success = process.returncode == 0
            else:
                cmd = ["sudo", "dnf", "install", "-y"] + packages
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=timeout
                )
                success = result.returncode == 0
                stderr = result.stderr

        elif package_manager == "pacman":
            if user_password:
                cmd = ["sudo", "-S", "pacman", "-S", "--noconfirm"] + packages
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                _, stderr = process.communicate(
                    input=f"{user_password}\n", timeout=timeout
                )
                success = process.returncode == 0
            else:
                cmd = ["sudo", "pacman", "-S", "--noconfirm"] + packages
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=timeout
                )
                success = result.returncode == 0
                stderr = result.stderr
        else:
            return False, "Unknown package manager"

        if success:
            return True, ""
        else:
            return False, stderr

    except subprocess.TimeoutExpired:
        return False, "Installation timed out"
    except Exception as e:
        return False, str(e)
