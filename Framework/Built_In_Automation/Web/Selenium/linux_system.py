import os
import shutil
import subprocess
from pathlib import Path


class LinuxSystemHelper:
    def __init__(self):
        self.os_release = self._load_os_release()

    def _load_os_release(self):
        data = {}
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    data[key] = value.strip().strip('"').strip("'")
        except Exception:
            return {}
        return data

    def is_ubuntu_version_at_least(self, major, minor=0):
        distro_id = self.os_release.get("ID", "").lower()
        version_id = self.os_release.get("VERSION_ID", "")

        version_parts = version_id.split(".")
        current_major = (
            int(version_parts[0])
            if len(version_parts) > 0 and version_parts[0].isdigit()
            else 0
        )
        current_minor = (
            int(version_parts[1])
            if len(version_parts) > 1 and version_parts[1].isdigit()
            else 0
        )

        return distro_id == "ubuntu" and (current_major, current_minor) >= (
            major,
            minor,
        )

    def is_gui_environment(self):
        return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))

    def is_gnome_session(self):
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        session = os.environ.get("DESKTOP_SESSION", "").lower()
        return "gnome" in desktop or "gnome" in session

    def supports_sudo_askpass(self):
        if not shutil.which("sudo"):
            return False

        try:
            result = subprocess.run(
                ["sudo", "-h"],
                capture_output=True,
                text=True,
                check=False,
            )
            help_output = f"{result.stdout}\n{result.stderr}".lower()
            return "askpass" in help_output and "-a" in help_output
        except Exception:
            return False

    def get_privilege_escalation_command(self):
        if (
            self.is_gui_environment()
            and self.is_gnome_session()
            and shutil.which("pkexec")
        ):
            return ["pkexec"], "pkexec"

        askpass = os.environ.get("SUDO_ASKPASS", "")
        if (
            self.is_gui_environment()
            and self.supports_sudo_askpass()
            and askpass
            and Path(askpass).exists()
            and shutil.which("sudo")
        ):
            return ["sudo", "-A"], "sudo -A"

        return ["sudo"], "sudo"

    def _is_package_available(self, package):
        try:
            result = subprocess.run(
                ["apt-cache", "policy", package],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return False

            output = f"{result.stdout}\n{result.stderr}".lower()
            if "candidate:" not in output:
                return False

            for line in output.splitlines():
                if line.strip().startswith("candidate:"):
                    candidate = line.split(":", 1)[1].strip()
                    return candidate != "(none)"

            return False
        except Exception:
            return False

    def _pick_available_package(self, package_options):
        for package_name in package_options:
            if self._is_package_available(package_name):
                return package_name
        return None

    def get_chrome_dependency_packages(self):
        dependencies = [
            ["libnss3"],
            ["libxss1"],
            ["libappindicator3-1"],
            ["fonts-liberation"],
            ["libasound2t64", "libasound2"],
            ["libnspr4"],
            ["libx11-xcb1"],
            ["libxcomposite1"],
            ["libxcursor1"],
            ["libxdamage1"],
            ["libxi6"],
            ["libxtst6"],
            ["libglib2.0-0t64", "libglib2.0-0"],
            ["libgtk-3-0t64", "libgtk-3-0"],
            ["libgdk-pixbuf2.0-0", "libgdk-pixbuf-xlib-2.0-0"],
            ["libxrandr2"],
            ["libpangocairo-1.0-0"],
            ["libatk1.0-0t64", "libatk1.0-0"],
            ["libcairo-gobject2"],
            ["xvfb"],
            ["ca-certificates"],
            ["libatk-bridge2.0-0t64", "libatk-bridge2.0-0"],
            ["libdrm2"],
            ["libxkbcommon0"],
            ["lsb-release"],
            ["wget"],
            ["xdg-utils"],
        ]

        selected_packages = []
        for package_group in dependencies:
            selected = self._pick_available_package(package_group)
            if selected:
                selected_packages.append(selected)
            else:
                print(
                    "Warning: Could not resolve package from options: "
                    f"{', '.join(package_group)}"
                )

        return selected_packages

    def _is_package_installed(self, package):
        try:
            result = subprocess.run(
                ["dpkg-query", "-W", "-f=${Status}", package],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return False
            return "install ok installed" in result.stdout.lower()
        except Exception:
            return False

    def get_missing_packages(self, packages):
        return [
            package for package in packages if not self._is_package_installed(package)
        ]
