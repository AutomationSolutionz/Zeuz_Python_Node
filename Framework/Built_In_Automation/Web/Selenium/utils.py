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


BASE_DIR = Path.home() / "test_automation_browsers"


class ChromeForTesting:
    CHROME_BASE_DIR = BASE_DIR / "chrome_for_testing"
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
        else:
            raise OSError(f"Unsupported platform: {self.system}/{self.arch}")
        
        self.CHROME_BASE_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROME_VERSIONS_DIR.mkdir(exist_ok=True)
        
        if not self.CHROME_INFO_FILE.exists():
            self._init_info_file()

    def _init_info_file(self):
        """Initialize the info.json file with default structure"""
        info = {
            "latest": {
                "version": "",
                "last_check": ""
            },
            "installed_versions": {} # ex: ("132.0.6763.0" : "2025-07-02")  <-- (version : last run) 
        }
        with open(self.CHROME_INFO_FILE, 'w') as f:
            json.dump(info, f, indent=4)

    def _load_info(self):
        """Load the info.json content"""
        if not self.CHROME_INFO_FILE.exists():
            return {
                "latest": {
                    "version": "", 
                    "last_check": ""
                },
                "installed_versions": {}
            }
        with open(self.CHROME_INFO_FILE, 'r') as f:
            return json.load(f)

    def _save_info(self, info):
        """Save data to info.json"""
        with open(self.CHROME_INFO_FILE, 'w') as f:
            json.dump(info, f, indent=4)

    def get_latest_version(self, channel="Stable", force_check=False):
        """Get the latest Chrome version with caching"""
        info = self._load_info()
        latest_info = info.get("latest", {})
        cached_version = latest_info.get("version", "")
        last_check_str = latest_info.get("last_check", "")
        
        if last_check_str and not force_check:
            last_check = datetime.datetime.fromisoformat(last_check_str).date()
            if (datetime.date.today() - last_check) <= timedelta(days=7):
                return cached_version
        
        # Fetch from API
        response = requests.get("https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json")
        response.raise_for_status()
        data = response.json()
        new_version = data['channels'][channel]['version']
        
        # Update info
        info["latest"] = {
            "version": new_version,
            "last_check": datetime.date.today().isoformat()
        }
        self._save_info(info)
        
        return new_version

    def get_download_url_for_version(self, version):
        """Get download URLs for specific Chrome version"""
        response = requests.get(
            "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        )
        response.raise_for_status()
        data = response.json()
        
        version_entry = next((v for v in data['versions'] if v['version'] == version), None)
        if not version_entry:
            raise Exception(f"Version {version} not found in known-good-versions")
        
        # Find Chrome URL
        chrome_entry = next(
            (item for item in version_entry['downloads']['chrome'] 
            if item['platform'] == self.platform_key),
            None
        )
        
        # Find ChromeDriver URL
        driver_entry = next(
            (item for item in version_entry['downloads']['chromedriver'] 
            if item['platform'] == self.platform_key),
            None
        )

        if not chrome_entry or not driver_entry:
            raise Exception(f"Download URLs not found for platform: {self.platform_key}")
        
        return chrome_entry['url'], driver_entry['url']

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
            return chrome_dir / chrome_dir_name / "Google Chrome for Testing.app" / "Contents" / "MacOS" / "Google Chrome for Testing"
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

    def download_file(self, url):
        """Download file from URL"""
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    def extract_zip(self, content, target_dir):
        """Extract ZIP content to target directory"""
        with zipfile.ZipFile(io.BytesIO(content)) as zip_ref:
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
        """Remove versions not used in the last 90 days"""
        info = self._load_info()
        installed_versions = info.get("installed_versions", {})
        today = datetime.date.today()
        cutoff_date = today - timedelta(days=90)
        
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
        
        # Download and extract Chrome
        print(f"Downloading Chrome for Testing {version}...")
        chrome_content = self.download_file(chrome_url)
        print(f"Extracting Chrome to {version_dir / 'chrome'}...")
        self.extract_zip(chrome_content, version_dir / "chrome")
        
        # Download and extract ChromeDriver
        print(f"Downloading ChromeDriver {version}...")
        driver_content = self.download_file(driver_url)
        print(f"Extracting ChromeDriver to {version_dir / 'driver'}...")
        self.extract_zip(driver_content, version_dir / "driver")

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

        if version and version < "115.0.5763.0":
            print("Chrome for testing version must be at least: '115.0.5763.0'")
            return None, None
        
        # Use latest version if not specified
        if not version:
            version = self.get_latest_version(channel=channel, force_check=True)
            print(f"Using latest chrome for testing version: {channel or ''} {version}")
        else:
            print(f"Using specified chrome for testing version: {version}")

        # Install if not already installed
        if not self.is_version_installed(version):
            print(f"Chrome for testing version {version} is not installed. Downloading...")
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
if __name__ == "__main__":
    version = input("Enter version (leave empty for latest): ").strip() or None
    cft = ChromeForTesting()
    chrome_bin, driver_bin = cft.setup_chrome_for_testing(version=version)

    if not chrome_bin or not driver_bin:
        print("Failed to setup Chrome for testing")
        sys.exit(1)

    print(f"Chrome binary: {chrome_bin}")
    print(f"ChromeDriver binary: {driver_bin}")

    options = Options()
    options.binary_location = str(chrome_bin)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    service = Service(str(driver_bin))

    print("Launching Selenium with Chrome for Testing...")
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://example.com/")
        print("Title of the page:", driver.title)
        time.sleep(10)
        driver.quit()
    except Exception as e:
        print("Selenium test failed:", str(e))



# TODO
# open telemetric
# logging in python
