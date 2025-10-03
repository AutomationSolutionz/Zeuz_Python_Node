#!/usr/bin/env python3
import os
import platform
import subprocess
import tarfile
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

# This should always be the latest LTS version
NODE_VERSION = "22.20.0"


def get_node_url():
    """Get Node.js download URL based on OS and architecture."""
    system = platform.system().lower()
    arch = platform.machine().lower()

    if system == "darwin":
        os_name = "darwin"
        ext = "tar.gz"
    elif system == "linux":
        os_name = "linux"
        ext = "tar.xz"
    elif system == "windows":
        os_name = "win"
        ext = "zip"
    else:
        raise Exception(f"Unsupported OS: {system}")

    if arch in ["x86_64", "amd64"]:
        arch = "x64"
    elif arch in ["arm64", "aarch64"]:
        arch = "arm64"
    else:
        raise Exception(f"Unsupported architecture: {arch}")

    return f"https://nodejs.org/dist/v{NODE_VERSION}/node-v{NODE_VERSION}-{os_name}-{arch}.{ext}"


def get_node_dir():
    """Get Node.js installation directory."""
    return Path.home() / ".zeuz" / "nodejs"


def extract_archive(archive_path, dest_dir):
    """Extract tar.gz, tar.xz, or zip archive."""
    if archive_path.suffix == ".zip":
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            # Get root directory name
            root_dir = zip_ref.namelist()[0].split("/")[0]
            for member in zip_ref.namelist():
                if member.startswith(root_dir + "/"):
                    # Remove root directory from path
                    target_path = dest_dir / Path(member).relative_to(root_dir)
                    if member.endswith("/"):
                        target_path.mkdir(parents=True, exist_ok=True)
                    else:
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with (
                            zip_ref.open(member) as source,
                            open(target_path, "wb") as target,
                        ):
                            target.write(source.read())
    else:
        with tarfile.open(archive_path, "r:*") as tar:
            # Get root directory name
            root_dir = tar.getnames()[0].split("/")[0]
            for member in tar.getmembers():
                if member.name.startswith(root_dir + "/"):
                    # Remove root directory from path
                    member.name = str(Path(member.name).relative_to(root_dir))
                    tar.extract(member, dest_dir)


def install_nodejs():
    """Download and install Node.js locally."""
    node_dir = get_node_dir()

    # Check if already installed
    node_bin = node_dir / ("node.exe" if platform.system() == "Windows" else "bin/node")
    if node_bin.exists():
        print("Node.js already installed")
        return

    print(f"Installing Node.js v{NODE_VERSION}...")

    # Create installation directory
    node_dir.mkdir(parents=True, exist_ok=True)

    # Download Node.js
    url = get_node_url()
    archive_name = Path(url).name
    archive_path = node_dir / archive_name

    print("Downloading Node.js...")
    urlretrieve(url, archive_path)

    try:
        # Extract Node.js
        print("Extracting Node.js...")
        extract_archive(archive_path, node_dir)
        print("Node.js installation completed")
    finally:
        # Clean up
        if archive_path.exists():
            archive_path.unlink()


def get_npm_path():
    """Get npm binary path."""
    node_dir = get_node_dir()
    if platform.system() == "Windows":
        return node_dir / "npm.cmd"
    else:
        return node_dir / "bin" / "npm"


def get_appium_path():
    """Get appium binary path."""
    node_dir = get_node_dir()
    if platform.system() == "Windows":
        return node_dir / "appium.cmd"
    else:
        return node_dir / "bin" / "appium"


def install_appium():
    """Install Appium and drivers using local Node.js."""
    npm_path = get_npm_path()

    if not npm_path.exists():
        raise Exception("npm not found. Install Node.js first.")

    print("Installing Appium...")
    subprocess.run([str(npm_path), "install", "-g", "appium"], check=True)

    # Install platform-specific drivers
    appium_path = get_appium_path()
    system = platform.system().lower()

    drivers_to_install = []
    if system == "windows":
        drivers_to_install = ["uiautomator2", "windows"]
    elif system == "darwin":
        drivers_to_install = ["uiautomator2", "xcuitest", "mac2"]
    elif system == "linux":
        drivers_to_install = ["uiautomator2"]

    print("Installing Appium drivers...")
    for driver in drivers_to_install:
        try:
            subprocess.run([str(appium_path), "driver", "install", driver], check=True)
            print(f"Successfully installed {driver} driver")
        except subprocess.CalledProcessError:
            print(f"Warning: Failed to install {driver} driver, continuing...")

    print("Appium installation completed")


def update_path():
    """Add Node.js binaries to PATH."""
    node_dir = get_node_dir()
    if platform.system() == "Windows":
        bin_dir = str(node_dir)
    else:
        bin_dir = str(node_dir / "bin")

    current_path = os.environ.get("PATH", "")
    if bin_dir not in current_path:
        os.environ["PATH"] = f"{bin_dir}{os.pathsep}{current_path}"


def get_required_drivers():
    """Get list of required drivers for current platform."""
    system = platform.system().lower()
    if system == "windows":
        return ["uiautomator2", "windows"]
    elif system == "darwin":
        return ["uiautomator2", "xcuitest", "mac2"]
    elif system == "linux":
        return ["uiautomator2"]
    return []


def check_appium_drivers():
    """Check if required Appium drivers are installed."""
    appium_path = get_appium_path()
    if not appium_path.exists():
        return []

    try:
        result = subprocess.run(
            [str(appium_path), "driver", "list", "--installed"],
            capture_output=True,
            text=True,
        )
        installed_drivers = []
        for line in result.stdout.split("\n"):
            if "@" in line and "installed" in line.lower():
                driver_name = line.split("@")[0].strip()
                installed_drivers.append(driver_name)
        return installed_drivers
    except:  # noqa: E722
        return []


def check_installations():
    """Check if Node.js, Appium and required drivers are installed."""
    node_dir = get_node_dir()
    node_bin = node_dir / ("node.exe" if platform.system() == "Windows" else "bin/node")

    # Check for Appium in global npm modules
    npm_path = get_npm_path()
    appium_installed = False

    if npm_path.exists():
        try:
            result = subprocess.run(
                [str(npm_path), "list", "-g", "appium"], capture_output=True, text=True
            )
            appium_installed = "appium@" in result.stdout
        except:  # noqa: E722
            pass

    # Check drivers
    required_drivers = get_required_drivers()
    installed_drivers = check_appium_drivers() if appium_installed else []
    missing_drivers = [d for d in required_drivers if d not in installed_drivers]

    return node_bin.exists(), appium_installed, missing_drivers


def install_missing_drivers(missing_drivers):
    """Install missing Appium drivers."""
    appium_path = get_appium_path()

    print("Installing missing Appium drivers...")
    for driver in missing_drivers:
        try:
            subprocess.run([str(appium_path), "driver", "install", driver], check=True)
            print(f"Successfully installed {driver} driver")
        except subprocess.CalledProcessError:
            print(f"Warning: Failed to install {driver} driver, continuing...")


def setup_nodejs_appium():
    """Main setup function."""
    try:
        print("Checking Node.js and Appium installation...")
        node_installed, appium_installed, missing_drivers = check_installations()

        if not node_installed:
            install_nodejs()
        else:
            print("Node.js already installed")

        update_path()

        if not appium_installed:
            install_appium()
        elif missing_drivers:
            install_missing_drivers(missing_drivers)
        else:
            print("Appium and all required drivers already installed")

        print("Node.js and Appium setup completed successfully")
        return True
    except Exception as e:
        print(f"Error during setup: {e}")
        return False


if __name__ == "__main__":
    setup_nodejs_appium()
