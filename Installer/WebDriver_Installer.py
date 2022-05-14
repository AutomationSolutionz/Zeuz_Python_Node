import os
import sys
from pathlib import Path
sys.path.append("..")

from Framework.Utilities import CommonUtil, ConfigModule

# Disable WebdriverManager SSL verification.
os.environ['WDM_SSL_VERIFY'] = '0'

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.microsoft import IEDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    from webdriver_manager.opera import OperaDriverManager
except:
    print("Could not find module webdriver-manager. Install by running command:")
    print("> pip install webdriver-manager")
    print("Press any key or [ENTER] to exit.")
    input()
    sys.exit()
# try:
#     import webdrivermanager
# except:
#     print("Could not find module webdrivermanager. Install by running command:")
#     print("> pip install webdrivermanager")
#     print("Press any key or [ENTER] to exit.")
#     input()

location = Path(os.getcwd()).parent/"Framework"/"settings.conf"
def update():
    try:
        path = ChromeDriverManager().install()
        print("Downloaded Chrome driver into:", path)
        ConfigModule.add_config_value("Selenium_driver_paths", "chrome_path", path, location)
    except:
        print(sys.exc_info())

    try:
        path = GeckoDriverManager().install()
        print("Downloaded Firefox driver into:", path)
        ConfigModule.add_config_value("Selenium_driver_paths", "firefox_path", path, location)
    except:
        print(sys.exc_info())

    try:
        path = EdgeChromiumDriverManager().install()
        print("Downloaded Edge driver into:", path)
        ConfigModule.add_config_value("Selenium_driver_paths", "edge_path", path, location)
    except:
        print(sys.exc_info())

    try:
        path = OperaDriverManager().install()
        print("Downloaded Opera driver into:", path)
        ConfigModule.add_config_value("Selenium_driver_paths", "opera_path", path, location)
    except:
        print(sys.exc_info())

    try:
        path = IEDriverManager().install()
        print("Downloaded Internet Explorer driver into:", path)
        ConfigModule.add_config_value("Selenium_driver_paths", "ie_path", path, location)
    except:
        print(sys.exc_info())


def update_old(pathname):
    driver_download_path = Path(pathname) / Path("webdrivers")
    drivers = webdrivermanager.AVAILABLE_DRIVERS

    for name in drivers:
        try:
            print("\n%s Driver..." % name.upper())
            driver = drivers[name](
                download_root=driver_download_path, link_path=pathname
            )
            if __name__ == "__main__":
                print("Specify the version number of %s driver and press [Enter].\n" % name +
                      "Press [Enter] for the latest version of %s driver \n" % name +
                      "Press [Space] + [Enter] to skip the downloading of %s driver " % name
                      )
                version = input()
                if len(version) == 0:
                    print("Downloading the latest version of %s driver. Please wait a bit..." % name)
                    driver.download_and_install()
                elif version == " ":
                    print("Skipping download of %s" % name)
                    continue
                else:
                    print("Downloading the %s version of %s driver. Please wait a bit..." % (version, name))
                    driver.download_and_install(version)
            else:
                print("Downloading the latest version of %s driver. Please wait a bit..." % name)
                driver.download_and_install()
        except RuntimeError:
            print("Skipping download of %s" % name)


def main():
    # Scripts folder is usually placed in the PATH. So we'll download the drivers there
    # PYTHON_DIR = os.path.dirname(sys.executable)
    # PYTHON_SCRIPTS_DIR = os.path.join(PYTHON_DIR, "Scripts")
    # print("Starting update. Drivers will be placed in the following directory:")
    # print("> %s" % PYTHON_SCRIPTS_DIR)
    update()

if __name__ == "__main__":
    main()
    print("\nUpdate complete. Press any key or [ENTER] to exit.")
    input()