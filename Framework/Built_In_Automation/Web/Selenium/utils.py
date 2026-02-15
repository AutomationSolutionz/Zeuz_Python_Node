import os
import sys
import json
import zipfile
import platform
import requests
import io
import shutil
import stat
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import subprocess
import datetime
from datetime import timedelta
import struct
import urllib.request
from rich.progress import Progress
from settings import ZEUZ_NODE_DOWNLOADS_DIR

try:
    from .linux_system import LinuxSystemHelper
except ImportError:
    from linux_system import LinuxSystemHelper


class ChromeForTesting:
    CHROME_BASE_DIR = ZEUZ_NODE_DOWNLOADS_DIR / "chrome_for_testing"
    CHROME_VERSIONS_DIR = CHROME_BASE_DIR / "versions"
    CHROME_INFO_FILE = CHROME_BASE_DIR / "info.json"

    def __init__(self):
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()

        if self.system == "windows":
            self.platform_key = "win64" if self.arch in ("amd64", "x86_64") else "win32"
        elif self.system == "darwin":
            self.platform_key = "mac-arm64" if self.arch == "arm64" else "mac-x64"
        elif self.system == "linux":
            self.platform_key = "linux64"
            self.linux_helper = LinuxSystemHelper()
            self._install_linux_dependencies()
        else:
            raise OSError(f"Unsupported platform: {self.system}/{self.arch}")

        if self.system != "linux":
            self.linux_helper = None

        self.CHROME_BASE_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROME_VERSIONS_DIR.mkdir(exist_ok=True)

        if not self.CHROME_INFO_FILE.exists():
            self._init_info_file()

    def _install_linux_dependencies(self):
        """Install Chrome dependencies for Ubuntu 24.04 and newer"""
        try:
            if self.linux_helper and self.linux_helper.is_ubuntu_version_at_least(
                24, 4
            ):
                deps = self.linux_helper.get_chrome_dependency_packages()
                if not deps:
                    print("Warning: No dependency packages resolved for Ubuntu.")
                    return

                missing_deps = self.linux_helper.get_missing_packages(deps)
                if not missing_deps:
                    print(
                        "Chrome dependencies already installed. Skipping apt install."
                    )
                    return

                privilege_cmd, privilege_mode = (
                    self.linux_helper.get_privilege_escalation_command()
                )
                print(
                    f"Installing Chrome dependencies for Ubuntu using {privilege_mode}..."
                )
                subprocess.run(privilege_cmd + ["apt-get", "update", "-qq"], check=True)
                subprocess.run(
                    privilege_cmd + ["apt-get", "install", "-y"] + missing_deps,
                    check=True,
                )
                print("Dependencies installed successfully.")
            else:
                return

        except Exception as e:
            print(f"Warning: Could not install dependencies: {e}")
            print("You may need to install Chrome dependencies manually.")

    def _init_info_file(self):
        # modification here to add settings to default structure
        """Initialize the info.json file with default structure"""
        info = {
            "latest": {"version": "", "last_check": ""},
            "installed_versions": {},  # ex: ("132.0.6763.0" : "2025-07-02")
            "settings": {
                "days_before_fetch": 15,  # set default fetch latest after 15 days
                "days_before_cleanup": 50,  # set default cleanup old versions after 50 days
            },
        }
        with open(self.CHROME_INFO_FILE, "w") as f:
            json.dump(info, f, indent=4)

    def _load_info(self):
        """Load the info.json content"""
        # modification here to use defaults with settings
        defaults = {
            "latest": {"version": "", "last_check": ""},
            "installed_versions": {},
            "settings": {"days_before_fetch": 15, "days_before_cleanup": 50},
        }

        if not self.CHROME_INFO_FILE.exists():
            return defaults

        with open(self.CHROME_INFO_FILE, "r") as f:
            info = json.load(f)

        # adds settings if missing
        if "settings" not in info:
            info["settings"] = defaults["settings"]
            self._save_info(info)

        return info

    def _save_info(self, info):
        """Save data to info.json"""
        with open(self.CHROME_INFO_FILE, "w") as f:
            json.dump(info, f, indent=4)

    def get_latest_version(self, channel="Stable", force_check=False):
        """Get the latest Chrome version with caching"""
        info = self._load_info()
        latest_info = info.get("latest", {})
        cached_version = latest_info.get("version", "")
        last_check_str = latest_info.get("last_check", "")

        # get days_before_fetch from settings
        settings = info.get("settings", {})

        # Check environment variable first
        env_fetch = os.environ.get("CHROME_DAYS_BEFORE_FETCH")
        if env_fetch:
            days_before_fetch = int(env_fetch)
            print(f"Using days_before_fetch from env: {days_before_fetch}")
        else:
            # otherwise use info.json or default
            days_before_fetch = settings.get("days_before_fetch", 15)

        # modification here to use settings for days_before_fetch
        if last_check_str and not force_check:
            last_check = datetime.datetime.fromisoformat(last_check_str).date()

            if (datetime.date.today() - last_check) <= timedelta(
                days=days_before_fetch
            ):
                return cached_version

        # Fetch from API
        response = requests.get(
            "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json",
            verify=False,
        )
        response.raise_for_status()
        data = response.json()
        new_version = data["channels"][channel]["version"]

        # Update info
        info["latest"] = {
            "version": new_version,
            "last_check": datetime.date.today().isoformat(),
        }
        self._save_info(info)

        return new_version

    def get_download_url_for_version(self, version):
        """Get download URLs for specific Chrome version"""
        response = requests.get(
            "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json",
            verify=False,
        )
        response.raise_for_status()
        data = response.json()

        version_entry = next(
            (v for v in data["versions"] if v["version"] == version), None
        )
        if not version_entry:
            raise Exception(f"Version {version} not found in known-good-versions")

        # Find Chrome URL
        chrome_entry = next(
            (
                item
                for item in version_entry["downloads"]["chrome"]
                if item["platform"] == self.platform_key
            ),
            None,
        )

        # Find ChromeDriver URL
        driver_entry = next(
            (
                item
                for item in version_entry["downloads"]["chromedriver"]
                if item["platform"] == self.platform_key
            ),
            None,
        )

        if not chrome_entry or not driver_entry:
            raise Exception(
                f"Download URLs not found for platform: {self.platform_key}"
            )

        return chrome_entry["url"], driver_entry["url"]

    def is_version_installed(self, version):
        """Check if version is installed and binaries exist"""
        info = self._load_info()
        installed_versions = info.get("installed_versions", {})

        # Check if version is in installed list
        if version not in installed_versions:
            return False

        # Verify binaries exist
        version_dir = self.CHROME_VERSIONS_DIR / version
        chrome_bin = self.get_chrome_binary_path(version_dir)
        driver_bin = self.get_driver_binary_path(version_dir)

        return chrome_bin.exists() and driver_bin.exists()

    def _update_installed_version_date(self, version):
        """Update the last used date for an installed version"""
        info = self._load_info()
        today = datetime.date.today().isoformat()

        info["installed_versions"][version] = today
        self._save_info(info)

    def get_chrome_binary_path(self, version_dir):
        """Get path to Chrome binary"""
        chrome_dir_name = f"chrome-{self.platform_key}"
        chrome_dir = version_dir / "chrome"

        if self.system == "windows":
            return chrome_dir / chrome_dir_name / "chrome.exe"
        elif self.system == "darwin":
            return (
                chrome_dir
                / chrome_dir_name
                / "Google Chrome for Testing.app"
                / "Contents"
                / "MacOS"
                / "Google Chrome for Testing"
            )
        elif self.system == "linux":
            return chrome_dir / chrome_dir_name / "chrome"
        return None

    def get_driver_binary_path(self, version_dir):
        """Get path to ChromeDriver binary"""
        driver_dir_name = f"chromedriver-{self.platform_key}"
        driver_dir = version_dir / "driver"

        if self.system == "windows":
            return driver_dir / driver_dir_name / "chromedriver.exe"
        else:
            return driver_dir / driver_dir_name / "chromedriver"

    def download_file(self, url, target_path, title):
        """Download file from URL"""
        response = requests.get(url, stream=True, verify=False)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))  # gets total size
        block_size = 1024  # 1 Kibibyte

        with open(target_path, "wb") as f, Progress() as progress:
            task = progress.add_task(title, total=total_size)

            for block in response.iter_content(block_size):  # block size 1K
                if block:
                    f.write(block)  # writes to file
                    progress.update(
                        task, advance=len(block)
                    )  # advances bar length by block size

        return target_path

    def extract_zip(
        self, content, target_dir
    ):  # modification here since path is passed instead of bytes
        """Extract ZIP content to target directory"""
        with zipfile.ZipFile(content) as zip_ref:
            for member in zip_ref.infolist():
                if member.is_dir():
                    continue

                extracted_path = zip_ref.extract(member, target_dir)

                perm = member.external_attr >> 16
                if perm:
                    os.chmod(extracted_path, perm)

    def set_execute_permissions(self, version_dir):
        """Set execute permissions for binaries (Unix systems)"""
        chrome_bin = self.get_chrome_binary_path(version_dir)
        driver_bin = self.get_driver_binary_path(version_dir)

        if self.system in ["linux", "darwin"]:
            # Set permissions
            if chrome_bin and chrome_bin.exists():
                chrome_bin.chmod(chrome_bin.stat().st_mode | stat.S_IEXEC)

            if driver_bin and driver_bin.exists():
                driver_bin.chmod(driver_bin.stat().st_mode | stat.S_IEXEC)

            if self.system == "darwin":
                app_path = chrome_bin.parent.parent.parent
                if app_path.exists():
                    try:
                        subprocess.run(["xattr", "-cr", str(app_path)], check=True)
                        print("Fixed macOS app permissions")
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to fix macOS permissions: {e}")

    def cleanup_old_versions(self):
        """Remove versions not used in the last X days (from settings)"""
        info = self._load_info()
        installed_versions = info.get("installed_versions", {})
        today = datetime.date.today()

        # get days_before_cleanup from  settings
        settings = info.get("settings", {})

        # Check environment variable first
        env_fetch = os.environ.get("CHROME_DAYS_BEFORE_CLEANUP")
        if env_fetch:
            days_before_cleanup = int(env_fetch)
            print(f"Using days_before_cleanup from env: {days_before_cleanup}")
        else:
            # otherwise use info.json or default
            days_before_cleanup = settings.get("days_before_cleanup", 50)

        # modification here to use settings for days_before_cleanup
        cutoff_date = today - timedelta(days=days_before_cleanup)

        versions_to_remove = []
        for version, date_str in installed_versions.items():
            if not date_str:
                continue

            last_used = datetime.date.fromisoformat(date_str)
            if last_used < cutoff_date:
                versions_to_remove.append(version)

        for version in versions_to_remove:
            version_dir = self.CHROME_VERSIONS_DIR / version
            if version_dir.exists():
                print(f"Cleaning up unused CfT version: {version}")
                shutil.rmtree(version_dir, ignore_errors=True)
            del installed_versions[version]

        if versions_to_remove:
            info["installed_versions"] = installed_versions
            self._save_info(info)
            print(f"Removed {len(versions_to_remove)} old versions of CfT")

    def install_version(self, version):
        """Install a specific Chrome version"""
        version_dir = self.CHROME_VERSIONS_DIR / version

        if version_dir.exists():
            shutil.rmtree(version_dir)
        version_dir.mkdir(parents=True)

        chrome_url, driver_url = self.get_download_url_for_version(version)

        chrome_zip_path = version_dir / "chrome.zip"

        # Download and extract Chrome
        print(f"Downloading Chrome for Testing {version}...")
        self.download_file(
            chrome_url, chrome_zip_path, title="Downloading Chrome"
        )  # download zip to path
        print(f"Extracting Chrome to {version_dir / 'chrome'}...")
        self.extract_zip(open(chrome_zip_path, "rb"), version_dir / "chrome")

        chrome_zip_path.unlink()  # remove zip

        driver_zip_path = version_dir / "driver.zip"

        # Download and extract ChromeDriver
        print(f"Downloading ChromeDriver {version}...")
        self.download_file(
            driver_url, driver_zip_path, title="Downloading ChromeDriver"
        )
        print(f"Extracting ChromeDriver to {version_dir / 'driver'}...")
        self.extract_zip(open(driver_zip_path, "rb"), version_dir / "driver")

        driver_zip_path.unlink()

        # Set execute permissions (Unix systems)
        self.set_execute_permissions(version_dir)

        # Update installed versions
        self._update_installed_version_date(version)
        print(f"\nSuccessfully installed Chrome for Testing {version}")
        print(f"Installation directory: {version_dir.resolve()}")

    def setup_chrome_for_testing(self, version=None, channel=None):
        """Setup Chrome for testing, install if necessary"""
        # Clean up old versions first
        self.cleanup_old_versions()

        if not channel:
            channel = "Stable"

        if version:
            if version < "115.0.5763.0":
                print("Chrome for testing version must be at least: '115.0.5763.0'")
                return None, None
            if version.strip().lower() == "system":
                print(
                    "Forcefully trying to use regular chrome instead of chrome for testing."
                )
                return None, None

        # Use latest version if not specified
        if not version:
            version = self.get_latest_version(channel=channel, force_check=False)
            print(f"Using latest chrome for testing version: {channel or ''} {version}")
        else:
            print(f"Using specified chrome for testing version: {version}")

        # Install if not already installed
        if not self.is_version_installed(version):
            print(
                f"Chrome for testing version {version} is not installed. Downloading..."
            )
            self.install_version(version)
        else:
            print(f"Chrome for testing version {version} already installed.")
            # Update last used date
            self._update_installed_version_date(version)

        version_dir = self.CHROME_VERSIONS_DIR / version
        chrome_bin = self.get_chrome_binary_path(version_dir)
        driver_bin = self.get_driver_binary_path(version_dir)

        if not chrome_bin.exists() or not driver_bin.exists():
            raise FileNotFoundError("Required binaries not found after installation")

        return chrome_bin, driver_bin


############################## Headed ##############################
# if __name__ == "__main__":
#     version = input("Enter version (leave empty for latest): ").strip() or None
#     cft = ChromeForTesting()
#     chrome_bin, driver_bin = cft.setup_chrome_for_testing(version=version)

#     if not chrome_bin or not driver_bin:
#         print("Failed to setup Chrome for testing")
#         sys.exit(1)

#     print(f"Chrome binary: {chrome_bin}")
#     print(f"ChromeDriver binary: {driver_bin}")

#     options = Options()
#     options.binary_location = str(chrome_bin)
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--window-size=1920,1080")

#     service = Service(str(driver_bin))

#     print("Launching Selenium with Chrome for Testing...")
#     try:
#         driver = webdriver.Chrome(service=service, options=options)
#         driver.get("https://example.com/")
#         print("Title of the page:", driver.title)
#         time.sleep(10)
#         driver.quit()
#     except Exception as e:
#         print("Selenium test failed:", str(e))


class ChromeExtensionDownloader:
    CHROME_EXTENSIONS_DIR = ZEUZ_NODE_DOWNLOADS_DIR / "chrome_extensions"
    CFT_INFO_FILE = ZEUZ_NODE_DOWNLOADS_DIR / "chrome_for_testing" / "info.json"
    DEFAULT_CHROME_VERSION = "138.0.7204.92"

    def __init__(self, chrome_version=None):
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()

        self.chrome_version = chrome_version or self._get_cft_version()
        self._setup_platform_info()
        self.output_dir = self.CHROME_EXTENSIONS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.CHROME_EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    def _get_cft_version(self):
        try:
            if self.CFT_INFO_FILE.exists():
                with open(self.CFT_INFO_FILE, "r") as f:
                    cft_info = json.load(f)
                    latest_version = cft_info.get("latest", {}).get("version", "")
                    if latest_version:
                        return latest_version
        except Exception as e:
            print(f"Warning: Could not read CfT info file: {e}")

        return self.DEFAULT_CHROME_VERSION

    def _setup_platform_info(self):
        if self.system == "windows":
            self.platform_os = "win"
        elif self.system == "darwin":
            self.platform_os = "mac"
        elif self.system == "linux":
            self.platform_os = "Linux"
        else:
            raise OSError(f"Unsupported platform: {self.system}")

        if "arm" in self.arch or "aarch" in self.arch:
            self.platform_arch = "arm"
        elif self.arch in ("x86_64", "amd64", "x64"):
            self.platform_arch = "x86-64"
        elif self.arch == "x86":
            self.platform_arch = "x86-32"
        else:
            self.platform_arch = "x86-64"

    def _build_download_url(self, extension_id):
        base_url = "https://clients2.google.com/service/update2/crx"
        params = [
            ("response", "redirect"),
            ("os", self.platform_os),
            ("arch", self.platform_arch),
            ("os_arch", self.platform_arch),
            ("prod", "chromecrx"),
            ("prodchannel", "unknown"),
            ("prodversion", self.chrome_version),
            ("acceptformat", "crx3"),
            ("x", f"id%3D{extension_id}%26uc"),
        ]
        query_string = "&".join([f"{k}={v}" for k, v in params])
        return f"{base_url}?{query_string}"

    def _get_download_headers(self, extension_id):
        return {
            "User-Agent": f"Mozilla/5.0 Chrome/{self.chrome_version}",
            "Referer": f"https://chrome.google.com/webstore/detail/{extension_id}",
        }

    def download_extension(self, extension_id, extract=False, keep_crx=True):
        print(
            f"Downloading extension '{extension_id}' for Chrome {self.chrome_version}..."
        )

        # Clean up first
        extension_dir = self.output_dir / extension_id
        if extension_dir.exists():
            shutil.rmtree(extension_dir)
        extension_dir.mkdir(parents=True, exist_ok=True)

        url = self._build_download_url(extension_id)
        headers = self._get_download_headers(extension_id)

        crx_path = extension_dir / f"{extension_id}.crx"

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                with open(crx_path, "wb") as f:
                    f.write(response.read())
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")

        if crx_path.stat().st_size == 0:
            crx_path.unlink()
            raise Exception("Downloaded file is empty")

        result = {
            "extension_id": extension_id,
            "chrome_version": self.chrome_version,
            "crx_path": str(crx_path),
            "extracted_path": None,
            "file_size": crx_path.stat().st_size,
        }

        if extract:
            extracted_path = self.extract_extension(crx_path)
            result["extracted_path"] = str(extracted_path)

            if not keep_crx:
                crx_path.unlink()
                result["crx_path"] = None

        return result

    def extract_extension(self, crx_path):
        crx_path = Path(crx_path)
        extract_path = crx_path.parent / crx_path.stem

        if extract_path.exists():
            shutil.rmtree(extract_path)

        try:
            with open(crx_path, "rb") as f:
                # Check CRX header
                magic = f.read(4)

                if magic == b"Cr24":  # CRX v3 format
                    # Skip header (version + header length fields)
                    f.read(8)
                    header_length = struct.unpack("<I", f.read(4))[0]
                    f.seek(16 + header_length)  # Skip to ZIP data
                elif magic[0:2] == b"PK":  # ZIP file format
                    f.seek(0)  # Rewind to start
                else:
                    raise Exception("Unknown file format - not a valid CRX file")

                # Extract ZIP contents
                with zipfile.ZipFile(f, "r") as zip_ref:
                    zip_ref.extractall(extract_path)

        except Exception as e:
            raise Exception(f"Extraction failed: {str(e)}")

        return extract_path

    def cleanup_extensions(self):
        if self.CHROME_EXTENSIONS_DIR.exists():
            if any(self.CHROME_EXTENSIONS_DIR.iterdir()):
                print(f"Cleaning up {self.CHROME_EXTENSIONS_DIR} directory...")
                shutil.rmtree(self.CHROME_EXTENSIONS_DIR)
                print("Cleanup complete.")
            else:
                shutil.rmtree(self.CHROME_EXTENSIONS_DIR)  # for safety
        self.CHROME_EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)

    def setup_chrome_extension_download(
        self, extension_id=None, extract=False, keep_crx=True
    ):
        print(f"Initializing Chrome Extension Downloader...")
        print(f"Using Chrome version: {self.chrome_version}")
        print(f"Output directory: {self.output_dir}")
        print(f"Platform: {self.platform_os} ({self.platform_arch})")

        if not extension_id:
            print("Extension ID is required")
            return None

        try:
            # Clean up any existing version before downloading
            extension_dir = self.output_dir / extension_id
            if extension_dir.exists():
                shutil.rmtree(extension_dir)

            # Download extension
            result = self.download_extension(
                extension_id, extract=extract, keep_crx=keep_crx
            )

            print(f"\nExtension {extension_id} downloaded successfully!")
            print(f"File size: {result['file_size']} bytes")

            if result.get("crx_path"):
                print(f"CRX file: {result['crx_path']}")

            if result.get("extracted_path"):
                print(f"Extracted to: {result['extracted_path']}")

            return result

        except Exception as e:
            print(f"Failed to download extension: {str(e)}")
            return None


############################## testing ############################
if __name__ == "__main__":
    extension_id = input("Enter Chrome Extension ID: ").strip()

    if not extension_id:
        print("Error: Extension ID is required")
        sys.exit(1)

    downloader = ChromeExtensionDownloader()
    result = downloader.setup_chrome_extension_download(extension_id=extension_id)

    if not result:
        print("Failed to download Chrome extension")
        sys.exit(1)
