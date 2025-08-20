
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
DOCKER_REPORTS_DIR = BASE_DIR / "reports"
DOCKER_LOGS_DIR = BASE_DIR / "logs"
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

def run_arachni_scan(target_url: str):
    """Run an Arachni scan using Docker container."""
    if not check_docker_available():
        print("Docker not available. Cannot run Arachni scan.")
        return
    
    print(f"Running Arachni scan on {target_url} via Docker...")
    
    # Ensure reports directory exists
    DOCKER_REPORTS_DIR.mkdir(exist_ok=True)
    
    try:
        # First, ensure the reports directory exists inside the Docker container
        print("Ensuring reports directory exists in Docker container...")
        mkdir_cmd = [
            'docker', 'exec', 'zeuz_arachni',
            'mkdir', '-p', '/home/arachni/arachni-ui/reports'
        ]
        subprocess.run(mkdir_cmd, capture_output=True, text=True, check=True)
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
        
    except subprocess.CalledProcessError as e:
        print(f"Arachni scan failed: {e}")
        print(f"Error output: {e.stderr}")
        raise
    except Exception as e:
        print(f"Unexpected error during Arachni scan: {e}")
        raise


def generate_report_from_afr(security_report_dir: Path):
    """Generate a report from the Docker container and copy to security report directory."""
    if not check_docker_available():
        print("Docker not available. Cannot generate report.")
        return False
    
    print("Generating report from Docker container...")
    
    # Ensure security report directory exists
    security_report_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Check if AFR file exists in Docker reports
        docker_afr = DOCKER_REPORTS_DIR / "output.afr"
        if not docker_afr.exists():
            print(f"AFR file not found at {docker_afr}")
            return False
        
        # Copy AFR file to security report directory
        security_afr = security_report_dir / "arachni_output.afr"
        shutil.copy2(docker_afr, security_afr)
        print(f"AFR file copied to {security_afr}")
        
        # Look for HTML report files (Arachni creates compressed HTML reports .html.zip)
        docker_html_files = list(DOCKER_REPORTS_DIR.glob("*.html*"))
        if docker_html_files:
            print(f"Found {len(docker_html_files)} HTML report files")
            # Copy HTML report to security report directory
            for html_file in docker_html_files:
                security_html = security_report_dir / f"arachni_{html_file.name}"
                shutil.copy2(html_file, security_html)
                print(f"HTML report copied to {security_html}")
            return True
        else:
            print("No HTML report files found. Checking for other report formats...")
            # Check for other report files that might have been generated
            report_files = list(DOCKER_REPORTS_DIR.glob("*"))
            print(f"Available files in reports directory: {[f.name for f in report_files]}")
            
            # Try to generate HTML report again if it wasn't created
            print("Attempting to regenerate HTML report...")
            try:
                report_cmd = [
                    'docker', 'exec', 'zeuz_arachni',
                    f'{DOCKER_ARACHNI_BIN}/arachni_reporter',
                    f'{DOCKER_REPORTS_PATH}/output.afr',
                    '--reporter=html:outfile=/home/arachni/arachni-ui/reports/arachni_report.html.zip'
                ]
                subprocess.run(report_cmd, capture_output=True, text=True, check=True)
                print("HTML report regenerated successfully")
                
                # Check again for HTML files (including compressed ones)
                docker_html_files = list(DOCKER_REPORTS_DIR.glob("*.html*"))
                if docker_html_files:
                    print(f"Found {len(docker_html_files)} HTML report files after regeneration")
                    for html_file in docker_html_files:
                        security_html = security_report_dir / f"arachni_{html_file.name}"
                        shutil.copy2(html_file, security_html)
                        print(f"HTML report copied to {security_html}")
                    return True
                else:
                    print("Still no HTML report files found after regeneration")
                    return False
            except Exception as e:
                print(f"Error regenerating HTML report: {e}")
                return False
            
    except Exception as e:
        print(f"Error generating report: {e}")
        return False
