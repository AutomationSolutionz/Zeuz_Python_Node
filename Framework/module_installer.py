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

executor = concurrent.futures.ThreadPoolExecutor()

def install_missing_modules():
    """
    Purpose: This function will check all the installed modules, compare with what is in requirements-win.txt file
    If anything is missing from requirements-win.txt file, it will install them only
    """
    try:
    
        print("\nmodule_installer: Checking for missing modules...")

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
                    req_list.append(i.split("==")[0])

        # get all the modules installed from freeze
        try:
            from pip._internal.operations import freeze
        except ImportError:
            # pip < 10.0
            from pip.operations import freeze

        freeze_list = freeze.freeze()
        alredy_installed_list = []
        for p in freeze_list:
            name = p.split("==")[0]
            if "@" not in name:
                # '@' symbol appears in some python modules in Windows
                alredy_installed_list.append(str(name).lower())

        # installing any missing modules
        installed = False
        for module_name in req_list:
            if module_name.lower() not in alredy_installed_list:
                try:
                    print("module_installer: Installing module: %s" % module_name)
                    subprocess.check_call([sys.executable, "-m", "pip", "install","--trusted-host=pypi.org", "--trusted-host=files.pythonhosted.org", module_name], stderr=DEVNULL, stdout=DEVNULL,)
                    print("module_installer: Installed missing module: %s" % module_name)
                    installed = True
                except:
                    print("module_installer: Failed to install module: %s" % module_name)

        if installed:
            print("module_installer: New modules installed.")
        else:
            print(
                "module_installer: All required modules are already installed. Continuing..."
            )
        
        # Upgrading outdated modules found in last run
        outdated_modules_filepath = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'outdated_modules.json'
        needs_to_be_updated = None
        if(os.path.exists(outdated_modules_filepath)):
            try:
                needs_to_be_updated = json.load(open(outdated_modules_filepath))
            except:
                traceback.print_exc()
            if(needs_to_be_updated):
                for module in needs_to_be_updated:
                    try:
                        module_name = module['name']
                        print("module_installer: Upgrading module: %s" % module_name)
                        subprocess.check_call([sys.executable, "-m", "pip", "install","--trusted-host=pypi.org", "--trusted-host=files.pythonhosted.org", module_name, "--upgrade"], stderr=DEVNULL, stdout=DEVNULL,)
                        print("module_installer: Upgraded outdated module: %s" % module_name)
                    except Exception as e:
                        print(e)
                        print("module_installer: Failed to upgrade module: %s" % module_name)
        def get_outdated_modules(): 
            # Storing outdated modules to upgrade on the next run
            sleep(5)
            try:
                print("module_installer: Checking for outdated modules")
                p1 = subprocess.run([sys.executable, "-m",'pip','list','--outdated','--format','json'],capture_output=True)
                outdated_modules = json.loads(p1.stdout)
                update_required = [module for module in outdated_modules if module['name'] in req_list]

                with open(outdated_modules_filepath, 'w') as f:
                    json.dump(update_required, f)
                print("module_installer: Saved the list of outdated modules")
            except:
                print("Failed to gather outdated modules...")
                traceback.print_exc()

        executor.submit(get_outdated_modules)
    except:
        print("Failed to install missing modules...")
        traceback.print_exc()
