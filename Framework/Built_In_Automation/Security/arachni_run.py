
import shutil
import subprocess
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parents[2]
ARACHNI_DIR = BASE_DIR / "tools" / "security" / "arachni"
ARACHNI_EXECUTABLE = ARACHNI_DIR / "bin" / "arachni"
ARACHNI_REPORTER_EXECUTABLE = ARACHNI_DIR / "bin" / "arachni_reporter"
ARACHNI_ZIP_DIR = BASE_DIR / "Framework"
OUTPUT_FILE = ARACHNI_ZIP_DIR / "output.afr"


def run_arachni_scan(target_url: str):
    """Run an Arachni scan for the target website."""
    if not ARACHNI_EXECUTABLE.exists():
        print("Arachni is not installed or the path is incorrect.")
        return
    print(f"Running Arachni scan on {target_url}...")
    subprocess.run([str(ARACHNI_EXECUTABLE), target_url, "--report-save-path", str(OUTPUT_FILE)], check=True)
    print(f"Scan complete. Results saved to {OUTPUT_FILE}.")


def generate_report_from_afr(security_report_dir: Path):
    """Generate a report from the existing .afr file and delete the .afr file afterward."""
    if not OUTPUT_FILE.exists():
        print(f"{OUTPUT_FILE} not found.")
        return
    print(f"Generating HTML report from {OUTPUT_FILE}...")
    security_report_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(ARACHNI_REPORTER_EXECUTABLE), str(OUTPUT_FILE), "--reporter=html:"], check=True)
    zip_file = next((f for f in OUTPUT_FILE.parent.glob("*.html.zip")), None)
    if zip_file:
        generated_zip = zip_file
        destination = security_report_dir / zip_file.name
        shutil.move(str(generated_zip), str(destination))
        print(f"Moved {generated_zip} to {destination}")
        print(f"Deleting {OUTPUT_FILE}...")
        OUTPUT_FILE.unlink()
        print(f"{OUTPUT_FILE} deleted.")
    else:
        return False
