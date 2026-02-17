import subprocess
import sys


def check_min_python_version(min_python_version, show_warning=False):
    """
    Checks if the current Python version is greater than or equal to the minimum required version.
    If not, it will display a warning message.
    """
    import warnings

    version, subversion = list(map(int, min_python_version.split(".")))
    # Minimum required version
    required_version = (version, subversion)

    # Get the current Python version
    current_version = sys.version_info[:3]

    # Check if the current version is less than the required version
    if current_version < required_version:
        if not show_warning:
            sys.stderr.write(
                f"Python {required_version[0]}.{required_version[1]} or higher is required.\n"
            )
            sys.exit(1)
        else:
            warning_message = (
                f"Warning: You are using Python {current_version[0]}.{current_version[1]}. "
                f"Python {required_version[0]}.{required_version[1]} or higher is recommended. Please update your Python version by 28-02-2025."
            )
            # Show warning in yellow
            warnings.warn(f"\033[93m{warning_message}\033[0m")


def uv_operation(*commands: str):
    """
    Runs the given commands using the `uv` command-line tool.
    """
    process = subprocess.Popen(
        [
            "uv",
            *commands,
            "--trusted-host=pypi.org",
            "--trusted-host=pypi.python.org",
            "--trusted-host=files.pythonhosted.org",
        ],
        stdout=subprocess.PIPE,
        text=True,  # Ensure we're dealing with text, not bytes
    )

    for c in iter(lambda: process.stdout.read(1), ""):
        sys.stdout.write(c)

    process.wait()

    # Optionally, check the return code
    if process.returncode != 0:
        print(
            f"WARN: uv {commands} command failed with return code: {process.returncode}"
        )


def install_missing_modules(req_list: list | None = None):
    """Installs missing modules from pyproject.toml."""
    if req_list is None:
        return

    uv_operation("add", *req_list)


def update_outdated_modules():
    """Updates outdated modules."""
    uv_operation("sync")
