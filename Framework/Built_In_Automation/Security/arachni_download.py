import requests
import tarfile
import shutil
from tqdm import tqdm
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parents[2]
ARACHNI_DIR = BASE_DIR / "tools" / "security" / "arachni"
RELEASES_API = "https://api.github.com/repos/Arachni/arachni/releases/latest"

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
    """Check if Arachni is installed; if not, download and install the latest version."""
    try:
        if ARACHNI_DIR.exists():
            print(f"Arachni is already installed at {ARACHNI_DIR}")
            return True

        print("Arachni not found. Proceeding with download and installation...")
        download_url = get_latest_release_url()
        if not download_url:
            print("Failed to fetch the download URL.")
            return False
        print(f"Download URL: {download_url}")
        download_path = Path("/tmp/arachni.tar.gz")
        if not download_file_with_progress(download_url, download_path):
            print("Failed to download Arachni.")
            return False
        print("Extracting Arachni...")
        with tarfile.open(download_path, "r:gz") as tar:
            tar.extractall(path=Path("/tmp"))
        extracted_folder = next(name for name in Path("/tmp").iterdir() if name.name.startswith("arachni"))
        shutil.move(str(extracted_folder), ARACHNI_DIR)
        print(f"Arachni installed to {ARACHNI_DIR}")
        download_path.unlink()
        print("Installation complete.")
        return True
    except Exception as e:
        print(f"Error during installation: {e}")
        return False
    