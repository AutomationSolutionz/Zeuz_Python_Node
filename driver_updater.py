# Author: Mohammed Sazid Al Rashid

import os
import sys
from pathlib import Path

try:
    import webdrivermanager
except:
    print("Could not find module webdrivermanager. Install by running command:")
    print("> pip install webdrivermanager")
    print("Press any key or [ENTER] to exit.")
    input()


def update(pathname):
    driver_download_path = Path(pathname) / Path("webdrivers")
    drivers = webdrivermanager.AVAILABLE_DRIVERS

    for name in drivers:
        try:
            print("\nDownloading %s..." % name)
            driver = drivers[name](
                download_root=driver_download_path, link_path=pathname
            )
            if __name__ == "__main__":
                print("Specify the version number of %s driver. Simply press Enter if you want the latest version" % name)
                version = input()
                if len(version) == 0:
                    driver.download_and_install()
                else:
                    driver.download_and_install(version)
            else:
                driver.download_and_install()
        except RuntimeError:
            print("Skipping download of %s" % name)


def main():
    # Scripts folder is usually placed in the PATH. So we'll download the drivers there
    PYTHON_DIR = os.path.dirname(sys.executable)
    PYTHON_SCRIPTS_DIR = os.path.join(PYTHON_DIR, "Scripts")

    print("Starting update. Drivers will be placed in the following directory:")
    print("> %s" % PYTHON_SCRIPTS_DIR)
    update(pathname=PYTHON_SCRIPTS_DIR)

if __name__ == "__main__":
    main()
    print("\nUpdate complete. Press any key or [ENTER] to exit.")
    input()