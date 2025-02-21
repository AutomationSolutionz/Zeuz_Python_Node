import subprocess
from urllib.parse import urlparse
from pathlib import Path
from rich.console import Console
from rich.table import Table


def extract_target(url: str) -> str:
    """
    Extracts and cleans the target from a given URL to ensure compatibility with nmap.
    """
    parsed_url = urlparse(url)
    target = parsed_url.hostname or parsed_url.netloc
    if target.startswith("www."):
        target = target[4:]
    return target


def check_perl_installed() -> bool:
    """
    Checks if Perl is installed on the system by running 'perl -v'.
    """
    try:
        # Try running 'perl -v' to check if Perl is installed
        subprocess.run(["perl", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def display_table(data: list, headers: list, title: str = "Report") -> None:
    """
    Display a formatted table in the terminal.
    """
    print(f"\n{title.center(60, '-')}\n")
    console = Console()

    table = Table(title=title)

    for header in headers:
        table.add_column(header)

    for row in data:
        table.add_row(*map(str, row))

    console.print(table)


def save_report_to_file(output: str, directory: Path, filename: str) -> None:
    """
    Save the scan report to a file in the specified directory.
    Args:
        output (str): The content to save to the file.
        directory (Path): The directory where the file should be saved.
        filename (str): The name of the file to save.
    Raises:
        Exception: If the file cannot be written.
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / filename
        
        with file_path.open("w") as file:
            file.write(output.strip())
        
        print(f"Report saved successfully to {file_path}")
    except Exception as e:
        print(f"Failed to save report to {directory}: {e}")

