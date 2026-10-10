
import shutil
import subprocess
import os
import zipfile
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parents[2]
ARACHNI_DIR = BASE_DIR / "tools" / "security" / "arachni"
ARACHNI_EXECUTABLE = ARACHNI_DIR / "bin" / "arachni"
ARACHNI_REPORTER_EXECUTABLE = ARACHNI_DIR / "bin" / "arachni_reporter"
ARACHNI_ZIP_DIR = BASE_DIR / "Framework"
OUTPUT_FILE = ARACHNI_ZIP_DIR / "output.afr"

# Docker paths - corrected for original arachni/arachni image
DOCKER_ARACHNI_BIN = "/usr/local/arachni/bin"
DOCKER_REPORTS_PATH = "/home/arachni/arachni-ui/reports"

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

def run_arachni_scan(target_url: str, security_report_dir: Path = None):
    """Run an Arachni scan using Docker container and save reports to security_report_dir."""
    if not check_docker_available():
        print("Docker not available. Cannot run Arachni scan.")
        return
    
    print(f"Running Arachni scan on {target_url} via Docker...")
    
    # Use provided security_report_dir or create a temporary one
    if security_report_dir is None:
        security_report_dir = Path.cwd() / "temp_reports"
    
    # Ensure reports directory exists
    security_report_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # First, ensure the reports directory exists inside the Docker container
        print("Ensuring reports directory exists in Docker container...")
        mkdir_cmd = [
            'docker', 'exec', 'zeuz_arachni',
            'mkdir', '-p', '/home/arachni/arachni-ui/reports'
        ]
        subprocess.run(mkdir_cmd, capture_output=True, text=True)  # Remove check=True to handle existing dir
        print("Reports directory created/verified in Docker container")
        
        # Run scan using Docker container with correct paths
        scan_cmd = [
            'docker', 'exec', 'zeuz_arachni',
            f'{DOCKER_ARACHNI_BIN}/arachni',
            target_url,
            '--report-save-path', f'{DOCKER_REPORTS_PATH}/output.afr'
        ]
        
        print(f"Executing scan command: {' '.join(scan_cmd)}")
        result = subprocess.run(scan_cmd, capture_output=True, text=True, check=True)
        print("Scan completed successfully")
        print(f"Scan output: {result.stdout}")
        
        # Generate HTML report - specify output directory to avoid saving to root
        print("Generating HTML report...")
        report_cmd = [
            'docker', 'exec', 'zeuz_arachni',
            f'{DOCKER_ARACHNI_BIN}/arachni_reporter',
            f'{DOCKER_REPORTS_PATH}/output.afr',
            '--reporter=html:outfile=/home/arachni/arachni-ui/reports/arachni_report.html.zip'
        ]
        
        subprocess.run(report_cmd, capture_output=True, text=True, check=True)
        print("HTML report generated successfully")
        
        # Copy reports from Docker container to security_report_dir
        print("Copying reports to security report directory...")
        copy_afr_cmd = [
            'docker', 'cp', 'zeuz_arachni:/home/arachni/arachni-ui/reports/output.afr', 
            str(security_report_dir / 'arachni_output.afr')
        ]
        subprocess.run(copy_afr_cmd, capture_output=True, text=True, check=True)
        
        copy_html_cmd = [
            'docker', 'cp', 'zeuz_arachni:/home/arachni/arachni-ui/reports/arachni_report.html.zip', 
            str(security_report_dir / 'arachni_report.html.zip')
        ]
        subprocess.run(copy_html_cmd, capture_output=True, text=True, check=True)
        
        print(f"Reports copied to: {security_report_dir}")
        
    except subprocess.CalledProcessError as e:
        print(f"Arachni scan failed: {e}")
        print(f"Error output: {e.stderr}")
        raise
    except Exception as e:
        print(f"Unexpected error during Arachni scan: {e}")
        raise


def generate_report_from_afr(security_report_dir: Path):
    """This function is deprecated. Reports are now saved directly during scan execution."""
    print("Note: generate_report_from_afr is deprecated. Reports are now saved directly during scan execution.")
    return True
