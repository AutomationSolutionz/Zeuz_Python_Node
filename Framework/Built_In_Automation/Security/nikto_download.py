import requests
from pathlib import Path
import shutil
import zipfile
import io

CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parents[2]
NIKTO_DIR = BASE_DIR / "tools" / "security" / "nikto"


def check_and_download_nikto():
    # GitHub URL for Nikto
    NIKTO_REPO_URL = "https://github.com/sullo/nikto/archive/refs/heads/master.zip"

    # Check if the Nikto directory exists
    if not NIKTO_DIR.exists():
        print("Nikto directory not found. Downloading from GitHub...")
        try:
            response = requests.get(NIKTO_REPO_URL)
            response.raise_for_status()

            NIKTO_DIR.parent.mkdir(parents=True, exist_ok=True)

            # Extract the zip file into the NIKTO_DIR
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                # Extract all files to a temporary folder
                temp_dir = NIKTO_DIR.parent / "temp_nikto"
                zip_file.extractall(temp_dir)
                # Move the extracted content to the target directory
                extracted_folder = temp_dir / "nikto-master"
                shutil.move(str(extracted_folder), str(NIKTO_DIR))
                # Remove the temporary folder
                shutil.rmtree(temp_dir)
            print(f"Nikto successfully downloaded and extracted to {NIKTO_DIR}")
            return True
        except Exception as e:
            print(f"Failed to download or extract Nikto: {e}")
            return False
    else:
        return True

