import os
import subprocess
import sys
import traceback

# NULL output device for disabling print output of pip installs
try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')


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
    except:
        print("Failed to install missing modules...")
        traceback.print_exc()
