import os
import subprocess
import shutil
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from arachni_download import check_and_install_arachni
from nikto_download import check_and_download_nikto
from arachni_run import run_arachni_scan, generate_report_from_afr
from nmap_scan import nmap_scan_run
from helper import extract_target, check_perl_installed, display_table, save_report_to_file

from Framework.Utilities import ConfigModule

temp_config = os.path.join(
    os.path.join(
        os.path.abspath(__file__).split("Framework")[0],
        os.path.join(
            "AutomationLog", ConfigModule.get_config_value("Advanced Options", "_file")
        ),
    )
)



def port_scaning_nmap(data_set: list) -> str:
    if not shutil.which("nmap"):
        error_data = [
            ["Error", "nmap is not installed on your system."],
            ["Solution", "Please install it using the following link:"],
            ["Download Link", "https://nmap.org/download.html"],
        ]
        display_table(error_data, headers=["Message", "Details"], title="Nmap Error")
        return "zeuz_failed"

    target_url = next(item[2] for item in data_set if item[0] == "nmap")
    target = extract_target(target_url)

    try:
        security_report_dir = Path(ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_config)) / 'security_report'
        saved_files = nmap_scan_run(target, security_report_dir)
        xml_path = saved_files["xml"]
        txt_path = saved_files["txt"]
        html_path = saved_files["html"]
        return "passed"
    except subprocess.CalledProcessError as e:
        error_data = [
            ["Target URL", " ".join(target)],
            ["Error", e.stderr.strip()],
        ]
        display_table(error_data, headers=["Description", "Details"], title="Nmap Error")
        return "zeuz_failed"


def check_and_install_wapiti():
    """Check if wapiti is installed; if not, install it automatically (prefers uv/uvx)."""
    try:
        # If wapiti CLI exists, we're done
        if shutil.which("wapiti"):
            print("Wapiti is already installed and available in PATH")
            return True

        # If uvx/uv exists, we can run wapiti without installing
        if shutil.which("uvx") or shutil.which("uv"):
            print("Wapiti not installed; will run via uvx/uv without global installation")
            return True
        
        print("Wapiti not found. Attempting automatic installation...")
        platform = sys.platform
        
        # Show what we're going to try
        print(f"Platform detected: {platform}")
        if platform == "darwin":
            print("Will attempt Homebrew installation")
        elif platform == "win32":
            print("Will attempt pip installation")
        else:
            print("Will attempt system package manager installation")
        
        if platform == "darwin":  # macOS
            print("Detected macOS - attempting multiple installation methods...")
            
            # Method 1: Try Homebrew (main repository)
            print("Trying Homebrew main repository...")
            try:
                result = subprocess.run(['brew', 'install', 'wapiti'], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print("Successfully installed Wapiti via Homebrew")
                    refresh_path_for_homebrew()
                    if verify_wapiti_installation():
                        return True
                else:
                    print(f"Homebrew main repository failed: {result.stderr}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print("Homebrew not available")
            
            # Method 2: Try Homebrew with alternative name
            print("Trying Homebrew with alternative names...")
            alternative_names = ['wapiti3', 'wapiti-scanner']
            for alt_name in alternative_names:
                try:
                    result = subprocess.run(['brew', 'install', alt_name], 
                                          capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        print(f"Successfully installed {alt_name} via Homebrew")
                        refresh_path_for_homebrew()
                        # Check if this creates a wapiti command
                        if verify_wapiti_installation():
                            return True
                        else:
                            print(f"{alt_name} installed but wapiti command not found")
                except Exception:
                    continue
            
            # Method 3: Try pip3 installation (may fail on PyPI)
            print("Trying pip3 installation...")
            try:
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'wapiti'], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print("Successfully installed Wapiti via pip3")
                    if verify_wapiti_installation():
                        return True
                else:
                    print(f"Pip3 installation failed: {result.stderr}")
            except Exception as e:
                print(f"Pip3 installation error: {e}")
            
            # Method 4: Try pip3 with alternative names
            print("Trying pip3 with alternative names...")
            pip_alternatives = ['wapiti3', 'wapiti-scanner', 'python-wapiti']
            for alt_name in pip_alternatives:
                try:
                    result = subprocess.run([sys.executable, '-m', 'pip', 'install', alt_name], 
                                          capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        print(f"Successfully installed {alt_name} via pip3")
                        if verify_wapiti_installation():
                            return True
                except Exception:
                    continue
            
            print("All automatic installation methods failed")
            
            # Last resort: Try installing from source
            print("Attempting installation from source...")
            
            # Check if git is available
            if shutil.which("git"):
                if try_install_wapiti_from_source():
                    return True
            else:
                print("Git not available - attempting to install git first...")
                try:
                    result = subprocess.run(['brew', 'install', 'git'], 
                                          capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        print("Git installed successfully. Now trying source installation...")
                        refresh_path_for_homebrew()
                        if try_install_wapiti_from_source():
                            return True
                    else:
                        print("Failed to install git")
                except Exception as e:
                    print(f"Error installing git: {e}")
                
                print("Please install git manually: brew install git")
            
            return False
        
        elif platform == "win32":  # Windows
            print("Detected Windows - attempting pip installation...")
            try:
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'wapiti'], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    print("Successfully installed Wapiti via pip")
                    # Verify installation
                    if verify_wapiti_installation():
                        return True
                    else:
                        print("Installation succeeded but wapiti command not found in PATH")
                        return False
                else:
                    print(f"Pip installation failed: {result.stderr}")
                    return False
            except subprocess.TimeoutExpired:
                print("Pip installation timed out")
                return False
        
        else:  # Linux
            print("Detected Linux - attempting package manager installation...")
            # Try different package managers
            package_managers = [
                (['apt-get', 'update', '&&', 'apt-get', 'install', '-y', 'wapiti'], 'apt'),
                (['yum', 'install', '-y', 'wapiti'], 'yum'),
                (['dnf', 'install', '-y', 'wapiti'], 'dnf'),
                (['zypper', 'install', '-y', 'wapiti'], 'zypper'),
            ]
            
            for cmd, manager in package_managers:
                try:
                    print(f"Trying {manager}...")
                    if '&&' in cmd:
                        # Handle commands with && operator
                        result = subprocess.run(' '.join(cmd), shell=True, capture_output=True, text=True, timeout=300)
                    else:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        print(f"Successfully installed Wapiti via {manager}")
                        # Verify installation
                        if verify_wapiti_installation():
                            return True
                        else:
                            print("Installation succeeded but wapiti command not found in PATH")
                            return False
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    print("No package manager found or installation failed")
                    continue
        return False
        
    except Exception as e:
        print(f"Error during Wapiti installation: {e}")
        return False
    

def show_manual_wapiti_instructions():
    """Show manual installation instructions for different platforms."""
    platform = sys.platform
    
    if platform == "darwin":  # macOS
        instructions = [
            ["Platform", "macOS"],
            ["Method 1", "uvx --from git+https://github.com/wapiti-scanner/wapiti wapiti --version"],
            ["Method 2", "Pip: pip3 install wapiti OR pip3 install wapiti3"],
            ["Method 3", "Git: git clone https://github.com/wapiti-scanner/wapiti.git && pip install -e ./wapiti"],
            ["Method 4", "Download: https://github.com/wapiti-scanner/wapiti/releases"],
            ["Note", "uvx is recommended if you use uv"]
        ]
    elif platform == "win32":  # Windows
        instructions = [
            ["Platform", "Windows"],
            ["Method 1", "Pip: pip install wapiti"],
            ["Method 2", "Download from: https://wapiti.sourceforge.io/"],
            ["Note", "Pip installation is recommended for Windows"]
        ]
    else:  # Linux
        instructions = [
            ["Platform", "Linux"],
            ["Ubuntu/Debian", "sudo apt-get install wapiti"],
            ["CentOS/RHEL", "sudo yum install wapiti"],
            ["Fedora", "sudo dnf install wapiti"],
            ["OpenSUSE", "sudo zypper install wapiti"],
            ["Note", "Use your system's package manager"]
        ]
    
    print("\n" + "="*60)
    print("MANUAL WAPITI INSTALLATION INSTRUCTIONS")
    print("="*60)
    for instruction in instructions:
        print(f"{instruction[0]}: {instruction[1]}")
    print("="*60)

def refresh_path_for_homebrew():
    """Refresh PATH to include Homebrew binaries."""
    try:
        # Common Homebrew paths
        homebrew_paths = [
            "/opt/homebrew/bin",      # Apple Silicon
            "/usr/local/bin",         # Intel Mac
            "/opt/homebrew/sbin",     # Apple Silicon sbin
            "/usr/local/sbin",        # Intel Mac sbin
        ]
        
        current_path = os.environ.get('PATH', '')
        new_paths = []
        
        for path in homebrew_paths:
            if Path(path).exists() and path not in current_path:
                new_paths.append(path)
        
        if new_paths:
            os.environ['PATH'] = f"{':'.join(new_paths)}:{current_path}"
            print(f"Added to PATH: {new_paths}")
        else:
            print("No new Homebrew paths to add")
            
    except Exception as e:
        print(f"Error refreshing PATH: {e}")

def try_install_wapiti_from_source():
    """Try to install wapiti from source as a last resort."""
    try:
        print("Cloning wapiti from GitHub...")
        
        # Create a temporary directory for the source
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Clone the repository
            clone_cmd = ['git', 'clone', 'https://github.com/wapiti-scanner/wapiti.git', str(temp_path)]
            result = subprocess.run(clone_cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                print(f"Git clone failed: {result.stderr}")
                return False
            
            print("Repository cloned successfully. Installing...")
            
            # Change to the wapiti directory
            wapiti_dir = temp_path / "wapiti"
            if not wapiti_dir.exists():
                print("Wapiti directory not found after clone")
                return False
            
            # Install using pip
            install_cmd = [sys.executable, '-m', 'pip', 'install', '-e', str(wapiti_dir)]
            result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print("Successfully installed wapiti from source")
                if verify_wapiti_installation():
                    return True
                else:
                    print("Installation succeeded but wapiti command not found")
                    return False
            else:
                print(f"Source installation failed: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"Error during source installation: {e}")
        return False

def verify_wapiti_installation():
    """Verify that wapiti is properly available (binary or via uvx)."""
    try:
        # Direct binary available
        if shutil.which("wapiti"):
            print("✅ Wapiti found in PATH")
            try:
                result = subprocess.run(['wapiti', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"✅ Wapiti version: {result.stdout.strip()}")
                    return True
            except subprocess.TimeoutExpired:
                print("⚠️  Wapiti version check timed out")
                return False
        
        # Try uvx fallback (ephemeral run)
        uvx_cmd = None
        if shutil.which("uvx"):
            uvx_cmd = [
                "uvx", "--from", "git+https://github.com/wapiti-scanner/wapiti",
                "--with", "greenlet",
                "wapiti", "--version",
            ]
        elif shutil.which("uv"):
            uvx_cmd = [
                "uv", "tool", "run", "--from", "git+https://github.com/wapiti-scanner/wapiti",
                "--with", "greenlet",
                "wapiti", "--version",
            ]
        
        if uvx_cmd:
            try:
                result = subprocess.run(uvx_cmd, capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print(f"✅ Wapiti (via uvx) version: {result.stdout.strip()}")
                    return True
                else:
                    print(f"⚠️  uvx wapiti check failed: {result.stderr}")
            except Exception as e:
                print(f"⚠️  uvx wapiti check error: {e}")
        
        print("❌ Wapiti not available (binary or uvx)")
        return False
    except Exception as e:
        print(f"❌ Error verifying wapiti availability: {e}")
        return False

def build_wapiti_command(wapiti_action: str, target: str) -> list:
    """Build the command to run Wapiti, preferring uvx if binary is unavailable."""
    if shutil.which("wapiti"):
        return ["wapiti", f"-v={wapiti_action}", "-u", target]
    if shutil.which("uvx"):
        return [
            "uvx", "--from", "git+https://github.com/wapiti-scanner/wapiti",
            "--with", "greenlet",
            "wapiti", f"-v={wapiti_action}", "-u", target,
        ]
    if shutil.which("uv"):
        return [
            "uv", "tool", "run", "--from", "git+https://github.com/wapiti-scanner/wapiti",
            "--with", "greenlet",
            "wapiti", f"-v={wapiti_action}", "-u", target,
        ]
    # Fallback to expected binary name; subprocess will raise if not found
    return ["wapiti", f"-v={wapiti_action}", "-u", target]

def server_scaning_wapiti(data_set: list) -> str:
    # Ensure availability (binary or uvx/uv)
    if not check_and_install_wapiti():
        print("Failed to make Wapiti available. Please install it manually or ensure uv/uvx is installed.")
        return "zeuz_failed"
    
    target = next(item[2] for item in data_set if item[0] == 'wapiti')
    wapiti_action = next(item[2] for item in data_set if item[0] == 'verbosity')

    if not target.startswith(("http://", "https://")):
        target = "http://" + target

    command = build_wapiti_command(wapiti_action, target)

    # Set UTF-8 encoding
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    try:
        print(command)
        result = subprocess.run(command, capture_output=True, text=True, check=True, env=env)
        print("Command Output:", result.stdout)

        for line in result.stdout.splitlines():
            if "A report has been generated in the file" in line:
                report_path = line.split("in the file")[1].strip()
                break
        else:
            print("Report path not found in Wapiti output.")
            return "zeuz_failed"
        
        security_report_dir = Path(ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_config)) / 'security_report' / 'wapiti'
        os.makedirs(security_report_dir, exist_ok=True)
        destination_path = security_report_dir / os.path.basename(report_path)

        shutil.move(report_path, destination_path)
        print(f"Report moved to {destination_path}")

        return "passed"
    except subprocess.CalledProcessError as e:
        print("An error occurred while running wapiti:")
        print(f"Error code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        return "zeuz_failed"
    except FileNotFoundError:
        print("Wapiti command not found. This should not happen after automatic availability checks.")
        return "zeuz_failed"
    except Exception as e:
        print(f"Unexpected error running wapiti: {e}")
        return "zeuz_failed"


def server_scaning_arachni(data_set: list) -> str:
    arachni_target = next(item[2] for item in data_set if item[0] == 'arachni')
    success = check_and_install_arachni()
    if success:
        if not arachni_target.startswith(("http://", "https://")):
            arachni_target = "http://" + arachni_target
        run_arachni_scan(arachni_target)
        security_report_dir = Path(ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_config)) / 'security_report'
        generate_report_from_afr(security_report_dir)
        return "passed"
    else:
        print("***** Arachni setup failed. *****")
        return "zeuz_failed"

def server_scaning_nikto(data_set: list) -> str:
    """
    Runs Nikto scan if Perl is installed, otherwise provides installation instructions based on the platform.
    """
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../.."))

    # Ensure Nikto is downloaded and ready
    if not check_and_download_nikto():
        return "zeuz_failed"

    # Define paths after ensuring Nikto exists
    NIKTO_DIR = os.path.join(BASE_DIR, "tools", "security", "nikto", "program")
    NIKTO_SCRIPT_PATH = os.path.join(NIKTO_DIR, "nikto.pl")

    # Find the target for Nikto scan from the dataset
    try:
        nikto_target = next(item[2] for item in data_set if item[0] == 'nikto')
    except StopIteration:
        print("Error: No target specified for Nikto scan in the dataset.")
        return "zeuz_failed"

    # Check if Perl is installed
    if not check_perl_installed():
        # Provide Perl installation instructions based on the platform
        system_platform = sys.platform
        installation_data = []

        if system_platform == "win32":
            installation_data = [
                ["Message", "Perl is not installed on your system."],
                ["Solution", "Install Perl from the following link:"],
                ["Download Link", "https://strawberryperl.com/"]
            ]
            display_table(installation_data, headers=["Message", "Details"], title="Perl Installation (Windows)")
        elif system_platform == "darwin":
            installation_data = [
                ["Message", "Perl is not installed on your system."],
                ["Solution", "Install Perl using Homebrew:"],
                ["Command", "brew install perl"]
            ]
            display_table(installation_data, headers=["Message", "Details"], title="Perl Installation (macOS)")
        else:
            installation_data = [
                ["Message", "Perl is not installed on your system."],
                ["Solution", "Install Perl using your system's package manager:"],
                ["Command", "sudo apt install perl"]
            ]
            display_table(installation_data, headers=["Message", "Details"], title="Perl Installation (Linux)")
        return "zeuz_failed"

    # Check if the nikto.pl file exists
    if not os.path.exists(NIKTO_SCRIPT_PATH):
        error_data = [
            ["Error", f"Nikto script (nikto.pl) not found at {NIKTO_SCRIPT_PATH}."],
            ["Solution", "Ensure the script is located at the correct path."],
            ["Action", "Check if the Nikto repository was correctly cloned."]
        ]
        display_table(error_data, headers=["Message", "Details"], title="Nikto Error")
        return "zeuz_failed"

    try:
        # Run the Nikto scan
        nikto_command = ["perl", NIKTO_SCRIPT_PATH, "-h", nikto_target]
        print("Starting Nikto scan... Please wait, this may take a while.")
        result = subprocess.run(nikto_command, capture_output=True, text=True, check=True)

        # Save the output to a report file
        security_report_dir = Path(ConfigModule.get_config_value("sectionOne", "test_case_folder", temp_config)) / 'security_report'
        output_file_name = "nikto_scan_result.txt"
        save_report_to_file(result.stdout, security_report_dir, output_file_name)

        print(result.stdout)
        return "passed"

    except subprocess.CalledProcessError as e:
        print("An error occurred while running Nikto:")
        print(e.stderr)
        return "zeuz_failed"

    except Exception as e:
        print(f"Unexpected error: {e}")
        return "zeuz_failed"