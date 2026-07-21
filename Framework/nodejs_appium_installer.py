#!/usr/bin/env python3
import os
import platform
import subprocess
import tarfile
import zipfile
import shutil
from pathlib import Path
import json
import requests

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
    node_dir = Path.home() / ".zeuz" / "nodejs"
    node_dir.mkdir(parents=True, exist_ok=True)
    return node_dir


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
    response = requests.get(url, verify=False)
    response.raise_for_status()
    with open(archive_path, "wb") as out_file:
        out_file.write(response.content)

    try:
        # Extract Node.js
        print("Extracting Node.js...")
        extract_archive(archive_path, node_dir)
        print("Node.js installation completed")
    finally:
        # Clean up
        if archive_path.exists():
            archive_path.unlink()

    # Disable SSL verification for npm for environments that have proxies
    print("Disabling SSL certificate verification for proxied environments for npm")
    npm_path = get_npm_path()
    subprocess.run([str(npm_path), "config", "set", "strict-ssl", "false"], check=False)


def get_npm_path():
    """Get npm binary path."""
    node_dir = get_node_dir()
    if platform.system() == "Windows":
        return node_dir / "npm.cmd"
    else:
        return node_dir / "bin" / "npm"


def get_node_path():
    """Get the Node.js binary managed by ZeuZ."""
    node_dir = get_node_dir()
    if platform.system() == "Windows":
        return node_dir / "node.exe"
    return node_dir / "bin" / "node"


def get_appium_path():
    """Get appium binary path."""
    node_dir = get_node_dir()
    if platform.system() == "Windows":
        return node_dir / "appium.cmd"
    else:
        return node_dir / "bin" / "appium"


def get_local_node_env():
    """Build an environment that always resolves ZeuZ's Node.js before system Node.js."""
    env = os.environ.copy()
    node_dir = get_node_dir()
    bin_dir = node_dir if platform.system() == "Windows" else node_dir / "bin"
    path_parts = [
        part
        for part in env.get("PATH", "").split(os.pathsep)
        if part and Path(part) != bin_dir
    ]
    env["PATH"] = os.pathsep.join([str(bin_dir), *path_parts])
    return env


def _run_local(command, **kwargs):
    kwargs.setdefault("env", get_local_node_env())
    return subprocess.run(command, **kwargs)


def _command_error(result):
    output = (result.stderr or result.stdout or "").strip()
    return output[-1000:] if output else f"exit code {result.returncode}"


def install_drivers(drivers):
    """Install only missing Appium drivers and verify the resulting state."""
    requested = list(dict.fromkeys(drivers))
    if not requested:
        return True

    try:
        installed = set(check_appium_drivers())
    except Exception as exc:
        print(f"ERROR: Could not inspect installed Appium drivers: {exc}")
        return False

    for driver in requested:
        if driver in installed:
            print(f"Appium driver {driver} is already installed; skipping")
            continue

        print(f"Installing Appium driver {driver}...")
        try:
            result = _run_local(
                [str(get_appium_path()), "driver", "install", driver],
                capture_output=True,
                text=True,
                timeout=900,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            print(f"ERROR: Appium driver {driver} installation could not run: {exc}")
            return False

        if result.returncode != 0:
            # Another process may have installed it after our initial check.
            try:
                if driver in check_appium_drivers():
                    print(
                        f"Appium driver {driver} became available during installation"
                    )
                    installed.add(driver)
                    continue
            except Exception:
                pass
            print(
                f"ERROR: Failed to install Appium driver {driver}: "
                f"{_command_error(result)}"
            )
            return False

        print(f"Successfully installed Appium driver {driver}")
        installed.add(driver)

    try:
        verified = set(check_appium_drivers())
    except Exception as exc:
        print(f"ERROR: Could not verify Appium drivers after installation: {exc}")
        return False

    missing = [driver for driver in requested if driver not in verified]
    if missing:
        print(f"ERROR: Required Appium drivers are still missing: {', '.join(missing)}")
        return False
    return True


def install_appium():
    """Install Appium and drivers using local Node.js."""
    npm_path = get_npm_path()

    if not npm_path.exists():
        raise Exception("npm not found. Install Node.js first.")

    print("Installing Appium...")
    result = _run_local(
        [
            str(npm_path),
            "install",
            "-g",
            "appium",
            "--prefix",
            str(get_node_dir()),
            "--strict-ssl=false",
        ],
        capture_output=True,
        text=True,
        timeout=900,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Appium installation failed: {_command_error(result)}")

    appium_path = get_appium_path()
    version = _run_local(
        [str(appium_path), "--version"],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if version.returncode != 0:
        raise RuntimeError(
            f"Appium was installed but is not executable: {_command_error(version)}"
        )
    print(f"Appium {version.stdout.strip()} installed at {appium_path}")

    print("Installing Appium drivers...")
    if not install_drivers(get_required_drivers()):
        raise RuntimeError("One or more required Appium drivers could not be prepared")
    print("Appium installation completed")
    return True


def update_path():
    """Add Node.js binaries to PATH."""
    node_dir = get_node_dir()
    if platform.system() == "Windows":
        bin_dir = str(node_dir)
    else:
        bin_dir = str(node_dir / "bin")

    current_path = os.environ.get("PATH", "")
    path_parts = [part for part in current_path.split(os.pathsep) if part != bin_dir]
    os.environ["PATH"] = os.pathsep.join([bin_dir, *path_parts])


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
        result = _run_local(
            [str(appium_path), "driver", "list", "--installed", "--json"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(_command_error(result))
        drivers_data = json.loads(result.stdout)
        if not isinstance(drivers_data, dict):
            raise ValueError("Appium returned an invalid driver list")
        return [
            name
            for name, info in drivers_data.items()
            if isinstance(info, dict) and info.get("installed", False)
        ]
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        raise RuntimeError(f"Unable to query Appium drivers: {exc}") from exc


def check_installations():
    """Check if Node.js, Appium and required drivers are installed."""
    node_bin = get_node_path()
    node_installed = False
    if node_bin.exists():
        result = _run_local(
            [str(node_bin), "--version"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        node_installed = result.returncode == 0

    appium_path = get_appium_path()
    appium_installed = False
    if node_installed and appium_path.exists():
        result = _run_local(
            [str(appium_path), "--version"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        appium_installed = result.returncode == 0

    # Check drivers
    required_drivers = get_required_drivers()
    installed_drivers = check_appium_drivers() if appium_installed else []
    missing_drivers = [d for d in required_drivers if d not in installed_drivers]

    return node_installed, appium_installed, missing_drivers


def install_missing_drivers(missing_drivers):
    """Install missing Appium drivers."""
    print("Installing missing Appium drivers...")
    return install_drivers(missing_drivers)


def check_and_remove_global_appium():
    """Check for and remove existing global Appium installations not managed by us."""
    print("Checking for conflicting global Appium installations...")

    # Method 1: Check using 'which appium'
    appium_bin = shutil.which("appium")
    if appium_bin:
        appium_path = Path(appium_bin).resolve()
        node_dir = get_node_dir().resolve()

        try:
            # Check if appium is within our node directory
            appium_path.relative_to(node_dir)
            # If it is, we are good
        except ValueError:
            print(f"Found conflicting Appium at {appium_path}")
            print("Uninstalling old Appium version...")
            try:
                is_windows = platform.system() == "Windows"
                subprocess.run(
                    ["npm", "uninstall", "-g", "appium"], check=True, shell=is_windows
                )
                print("Successfully uninstalled conflicting Appium")
            except Exception as e:
                print(f"Warning: Failed to uninstall conflicting Appium: {e}")
            return

    # Method 2: Check using 'npm list -g appium' (if npm is available in system path)
    # This catches cases where appium is installed but not in PATH
    npm_bin = shutil.which("npm")
    if npm_bin:
        try:
            # Check if this npm is ours
            npm_path = Path(npm_bin).resolve()
            node_dir = get_node_dir().resolve()
            try:
                npm_path.relative_to(node_dir)
                # If it is our npm, skip this check as we handle our own appium
                return
            except ValueError:
                pass

            # Check for global appium using system npm
            is_windows = platform.system() == "Windows"
            result = subprocess.run(
                ["npm", "list", "-g", "--json", "appium"],
                capture_output=True,
                text=True,
                shell=is_windows,
            )
            npm_data = json.loads(result.stdout)
            if "appium" in npm_data.get("dependencies", {}):
                print("Found conflicting Appium in global npm modules")
                print("Uninstalling old Appium version...")
                subprocess.run(
                    ["npm", "uninstall", "-g", "appium"], check=True, shell=is_windows
                )
                print("Successfully uninstalled conflicting Appium")
        except Exception as e:
            # Don't fail if npm check fails, just log warning
            print(f"Warning: Failed to check/uninstall global Appium via npm: {e}")


def setup_nodejs_appium():
    """Main setup function."""
    try:
        check_and_remove_global_appium()
        update_path()  # Ensure Node.js is in PATH from the start

        os.environ["NODE_TLS_REJECT_UNAUTHORIZED"] = "0"
        os.environ["npm_config_strict_ssl"] = "false"

        print("Checking Node.js and Appium installation...")
        node_installed, appium_installed, missing_drivers = check_installations()

        if not node_installed:
            install_nodejs()
            update_path()  # Update PATH after installation
        else:
            print("Node.js already installed")

        if not appium_installed:
            install_appium()
        elif missing_drivers:
            if not install_missing_drivers(missing_drivers):
                raise RuntimeError(
                    "Required Appium drivers could not be installed: "
                    f"{', '.join(missing_drivers)}"
                )
        else:
            print("Appium and all required drivers already installed")

        node_installed, appium_installed, missing_drivers = check_installations()
        if not node_installed:
            raise RuntimeError("ZeuZ-managed Node.js could not be verified")
        if not appium_installed:
            raise RuntimeError("ZeuZ-managed Appium could not be verified")
        if missing_drivers:
            raise RuntimeError(
                "Required Appium drivers are missing after setup: "
                f"{', '.join(missing_drivers)}"
            )

        installed_drivers = check_appium_drivers()
        print(
            "Node.js and Appium setup verified successfully "
            f"(drivers: {', '.join(installed_drivers) or 'none'})"
        )
        return True
    except Exception as e:
        print(f"ERROR: Node.js/Appium setup was not completed: {e}")
        return False


if __name__ == "__main__":
    setup_nodejs_appium()
