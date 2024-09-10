import os
import subprocess
import sys
import traceback
import json
import concurrent.futures
from time import sleep
# NULL output device for disabling print output of pip installs
try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

def get_req_list():
    import platform

    plt = platform.system().lower()

    if "windows" in plt:
        req_file_name = "requirements-win.txt"
    elif "linux" in plt:
        req_file_name = "requirements-linux.txt"
    elif "darwin" in plt:
        req_file_name = "requirements-mac.txt"
    else:
        print("Unidentified system")
        return

    req_file_path = True
    if req_file_path:
        req_file_path = (
            os.path.dirname(os.path.abspath(__file__)).replace(
                os.sep + "Framework", ""
            )
            + os.sep
            + req_file_name
        )

    req_list = list()
    with open(req_file_path) as fd:
        for i in fd.read().splitlines():
            if not i.startswith("http"):
                req_list.append(i.strip())
    return req_list

def check_min_python_version(min_python_version,show_warning):
    import warnings
    version, subversion = list(map(int, min_python_version.split('.')))
    # Minimum required version
    required_version = (version, subversion)

    # Get the current Python version
    current_version = sys.version_info[:3]

    # Check if the current version is less than the required version
    if current_version < required_version:
        if not show_warning:
            sys.stderr.write(f"Python {required_version[0]}.{required_version[1]} or higher is required.\n")
            sys.exit(1)
        else:
            warning_message = (
                f"Warning: You are using Python {current_version[0]}.{current_version[1]}. "
                f"Python {required_version[0]}.{required_version[1]} or higher is recommended. Please update your Python version by 28-02-2025."
            )
            # Show warning in yellow
            warnings.warn(f"\033[93m{warning_message}\033[0m")

def install_missing_modules(req_list=None):
    """
    Purpose: This function will check all the installed modules, compare with what is in requirements-win.txt file
    If anything is missing from requirements-win.txt file, it will install them only
    """
    try:
        if req_list is None:
            req_list = get_req_list()
        # print("\nmodule_installer: Checking for missing modules...")

    

        # get all the modules installed from freeze
        try:
            from pip._internal.operations import freeze
        except ImportError:
            # pip < 10.0
            from pip.operations import freeze

        freeze_list = freeze.freeze()
        alredy_installed_list_version = []
        alredy_installed_list_no_version = []
        for p in freeze_list:
            name = p.split("==")[0]
            if "@" not in name:
                # '@' symbol appears in some python modules in Windows
                alredy_installed_list_version.append(str(p).lower())
                alredy_installed_list_no_version.append(str(name).lower())
        # installing any missing modules
        installed = False
        for module_name in req_list:
            if ("==" not in module_name.lower() and module_name.lower() not in alredy_installed_list_no_version) or ("==" in module_name.lower() and module_name.lower() not in alredy_installed_list_version):
                try:
                    print("module_installer: Installing module: %s" % module_name)
                    subprocess.check_call([
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "--trusted-host=pypi.org",
                        "--trusted-host=pypi.python.org",
                        "--trusted-host=files.pythonhosted.org",
                        module_name
                    ], stderr=DEVNULL, stdout=DEVNULL,)
                    print("module_installer: Installed missing module: %s" % module_name)
                    installed = True
                except:
                    print("module_installer: Failed to install module: %s" % module_name)

        if installed:
            print("module_installer: New modules installed.")
        else:
            print("module_installer: All required modules are already installed. Continuing...")
    except:
        print("Failed to install missing modules...")
        traceback.print_exc()

def update_outdated_modules(req_list = None):
    if req_list is None:
        req_list = get_req_list()
    # Upgrading outdated modules found in last run
    outdated_modules_filepath = os.path.dirname(os.path.abspath(__file__)).replace(os.sep + "Framework", os.sep + 'AutomationLog') + os.sep + 'outdated_modules.json'
    needs_to_be_updated = None
    if os.path.exists(outdated_modules_filepath):
        try:
            needs_to_be_updated = json.load(open(outdated_modules_filepath))
        except:
            traceback.print_exc()
        os.remove(outdated_modules_filepath)
        if needs_to_be_updated:
            for module in needs_to_be_updated:
                try:
                    module_name = module['name']
                    print("module_installer: Upgrading module: %s" % module_name)
                    subprocess.check_call([
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "--trusted-host=pypi.org",
                        "--trusted-host=pypi.python.org"
                        "--trusted-host=files.pythonhosted.org",
                        module_name,
                        "--upgrade"
                    ], stderr=DEVNULL, stdout=DEVNULL,)
                    print("module_installer: Upgraded outdated module: %s" % module_name)
                except Exception:
                    print("module_installer: Failed to upgrade module: %s" % module_name)
    def get_outdated_modules(): 
        # Storing outdated modules to upgrade on the next run
        sleep(15)
        try:
            # print("module_installer: Checking for outdated modules")
            pip_cmnd = subprocess.run([sys.executable, "-m",'pip','list','--outdated','--format','json'],capture_output=True)
            pip_stdout = pip_cmnd.stdout
            if type(pip_stdout) == bytes:
                pip_stdout = pip_stdout.decode("utf-8")
            outdated_modules = json.loads(pip_stdout.split("}]")[0] + "}]")
            update_required = [module for module in outdated_modules if module['name'] in req_list]

            with open(outdated_modules_filepath, 'w') as f:
                json.dump(update_required, f)
            # print("module_installer: Saved the list of outdated modules")
        except Exception:
            print("module_installer: Failed to gather outdated modules...")
    executor = concurrent.futures.ThreadPoolExecutor()
    executor.submit(get_outdated_modules)
    executor.shutdown(wait=False)


