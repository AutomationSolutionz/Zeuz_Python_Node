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


def server_scaning_wapiti(data_set: list) -> str:
    target = next(item[2] for item in data_set if item[0] == 'wapiti')
    wapiti_action = next(item[2] for item in data_set if item[0] == 'verbosity')

    if not target.startswith(("http://", "https://")):
        target = "http://" + target

    command = ["wapiti", f"-v={wapiti_action}", "-u", target]

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
        print(e.stderr)
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