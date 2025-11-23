import asyncio
import sys
import platform
import shutil
from typing import Tuple, List
import logging
from subprocess import CalledProcessError




class InstallerTools:
    """
    Collection of Python and system package installation-related utility functions 
    to be used in installation scripts.
    """
    def __init__(self) -> None:

        # OS name
        self.os_name = platform.system()

        # Setup logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter(
           "[node_installer - {levelname}] {asctime} - {funcName} - {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M",
        )
        if not self.logger.handlers:
            self.console_handler = logging.StreamHandler()
            self.logger.addHandler(self.console_handler)
            self.console_handler.setFormatter(self.formatter)
            # self.file_handler = logging.FileHandler("installer_utils.log", mode="a", encoding="utf-8")
            # self.logger.addHandler(self.file_handler)


    async def check_python_module_available(self, module_name: str) -> bool:
        """
        Check if a module is available for import

        Args:
            module_name (str): The name used to import the package

        Returns:
            bool: True if package is available, False otherwise
        """

        try:
            __import__(module_name)
            self.logger.info(f"{module_name} is available.")
            return True
        except ImportError:
            self.logger.info(f"{module_name} is not available.")
            return False


    async def add_python_package(self, package_name: str) -> Tuple[bool, str]:
        """
        Install a package using `uv add`

        Args:
            package_name (str): The name of the package to install

        Returns:
            bool: True if installation successful, False otherwise
            str: Error message if installation failed, otherwise empty string
        """

        # Installation command
        cmd = [sys.executable, "-m", "uv", "add", package_name]
        self.logger.debug(f"{cmd = }")
        message = ""

        try:
            self.logger.info(f"Installing {package_name}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Wait for the process to complete and capture output
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise CalledProcessError(
                    process.returncode,
                    cmd,
                    output=stdout,
                    stderr=stderr
                )
            self.logger.info(f"Successfully installed {package_name}.")

            if stdout:
                self.logger.debug(f"[stdout]\n{stdout.decode()}")
            return True, message

        except CalledProcessError as e:
            self.logger.exception(f"Failed to install {package_name}")
            if e.stderr:
                message = e.stderr.decode()
                self.logger.debug(f"[stderr]\n{message}")
            return False, message
        
        except FileNotFoundError:
            message = "Error: 'uv' command not found or Python interpreter path is incorrect."
            self.logger.exception(f"{message}")
            return False, message


    async def install_linux_packages(self, packages: List, password: str = ""):
        """
        Install Linux packages using apt.
        
        Args:
            packages (list): List of package names to install
            password (str, optional): Sudo password if required
        
        Returns:
            tuple: (bool, str) - (success_status, error_message)
        """
        self.logger.debug(f"{packages=}")

        if not packages:
            self.logger.warning("Empty package list received, no packages installed.")
            return True, "No packages to install"
        
        try:
            # Installation command
            package_manager = self._get_linux_package_manager()
            # -p '' to suppress the "[sudo] password for user:" prompt from stdout
            cmd = ["sudo", "-S", "-p", "", package_manager, "install", "-y"] + packages
            
            # Prepare the password input. newline to simulate the user pressing 'Enter'.
            if password:
                sudo_input = password + "\n"
            else:
                self.logger.warning("No password received. Attempting passwordless sudo...")
                sudo_input = "\n" 
            
            self.logger.info(f"Installing packages...")
            self.logger.debug(f"{cmd = }")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input=sudo_input.encode())
            
            # Decode output
            stdout_str = stdout.decode('utf-8') if stdout else ""
            stderr_str = stderr.decode('utf-8') if stderr else ""
            
            # Check if installation was successful
            if process.returncode == 0:
                self.logger.info(f"Successfully installed: {', '.join(packages)}")
                return True, ""
            else:
                error_msg = f"{stderr_str}\n{stdout_str}".strip()
                self.logger.error(f"Installation failed: {error_msg}")
                return False, error_msg
                
        except FileNotFoundError:
            error_msg = f"Error: sudo or {package_manager} command not found."
            self.logger.exception(error_msg)
            return False, error_msg
        
        except Exception as e:
            self.logger.exception("Unexpected exception")
            return False, f"Unexpected error: {str(e)}"


    class ValidationError(Exception):
        """Input validation exception"""
        pass


    def _sanitize_packages_list(self, packages: List) -> List:
        """Raises ValidationError exception if a ';' is detected in the packages list"""
        packages_str = " ".join(packages)
        self.logger.debug(f"{packages_str = }")
        if ";" in packages_str:
            raise self.ValidationError("Command chaining with ';' is not allowed.")
        else:
            return packages
        

    def _get_linux_package_manager(self) -> str:
        """Detect Linux package manager"""

        if self.os_name == 'Linux':
            if shutil.which("apt-get"):
                return "apt-get"
            elif shutil.which("dnf"):
                return "dnf"
            elif shutil.which("yum"):
                return "yum"
            elif shutil.which("pacman"):
                return "pacman"
            elif shutil.which("zypper"):
                return "zypper"
            elif shutil.which("apk"):
                return "apk"
            elif shutil.which("emerge"):
                return "emerge"
            elif shutil.which("nix"):
                return "nix"
            
        self.logger.warning("Checking for Linux package manager on non-Linux platform")
        return ""
    