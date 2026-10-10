import requests
import tarfile
import shutil
import subprocess
import sys
from tqdm import tqdm
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parents[2]
ARACHNI_DIR = BASE_DIR / "tools" / "security" / "arachni"
RELEASES_API = "https://api.github.com/repos/Arachni/arachni/releases/latest"

def check_docker_available():
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Check if Docker daemon is running
            result = subprocess.run(['docker', 'info'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def start_arachni_container():
    """Start the Arachni Docker container."""
    try:
        print("Starting Arachni Docker container...")
        
        # Check if container is already running
        result = subprocess.run(['docker', 'ps', '--filter', 'name=zeuz_arachni', '--format', '{{.Names}}'], 
                              capture_output=True, text=True, timeout=10)
        
        if 'zeuz_arachni' in result.stdout:
            print("Arachni container is already running")
            return True
        
        # Start the container using docker-compose
        compose_file = BASE_DIR / "docker-compose.yml"
        if not compose_file.exists():
            print("Docker Compose file not found. Please ensure docker-compose.yml exists in project root.")
            return False
        
        result = subprocess.run(['docker-compose', 'up', '-d'], 
                              cwd=BASE_DIR, 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("Arachni container started successfully")
            return True
        else:
            print(f"Failed to start container: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error starting Arachni container: {e}")
        return False

def download_file_with_progress(url, destination):
    """Download a file with a progress bar."""
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            with open(destination, 'wb') as file, tqdm(
                desc=f"Downloading {destination.name}",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
                    progress_bar.update(len(chunk))
            print(f"Downloaded file to {destination}")
            return True
        else:
            print(f"Failed to download file: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error during file download: {e}")
        return False


def get_latest_release_url():
    """Fetch the latest release details from GitHub API."""
    try:
        print("Fetching the latest release details from GitHub...")
        response = requests.get(RELEASES_API)
        if response.status_code == 200:
            release_data = response.json()
            for asset in release_data["assets"]:
                if "linux-x86_64.tar.gz" in asset["name"]:
                    return asset["browser_download_url"]
            print("No compatible Linux release found in the latest version.")
            return None
        else:
            print(f"Failed to fetch release details: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error while fetching release details: {e}")
        return None


def check_and_install_arachni():
    """Check if Arachni is available via Docker; if not, start the container."""
    if check_docker_available():
        print("Docker detected. Using Arachni container...")
        
        # Start the container if not running
        if start_arachni_container():
            print("Arachni is ready via Docker container")
            return True
        else:
            print("Failed to start Arachni container")
            return False
    else:
        print("Docker not available. Please install Docker first.")
        print("Download from: https://www.docker.com/products/docker-desktop")
        return False
    