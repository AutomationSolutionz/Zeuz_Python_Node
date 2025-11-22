from Framework.install_handler.utils import send_response
from Framework.install_handler.installer_tools import InstallerTools

tools = InstallerTools()

async def check_status():
    """Checks if mariadb Python library is installed."""

    if await tools.check_python_module_available("mariadb"):
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "MariaDB",
                "status": "installed",
                "comment": "MariaDB connector is installed.",
            }
        })
        return True
    else:
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "MariaDB",
                "status": "not installed",
                "comment": "Install mariadb to connect to MariaDB databases.",
            }
        })
        return False



async def install(user_password: str = ""):
    is_already_installed = await check_status()

    if not is_already_installed:
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "MariaDB",
                "status": "installing",
                "comment": "Downloading and installing, please wait...",
            }
        })

        # MariaDB dependencies installation required if on Linux (sudo password required)
        if tools.os_name == 'Linux':
            install_libmariadb, msg = await tools.install_linux_packages(
                packages=['libmariadb3', 'libmariadb-dev'], 
                password=user_password
            )
        else:
            # If not Linux, bypass dependency installation as it's not required
            install_libmariadb, msg = True, ""

        # If dependency installation was successful (or bypassed)
        if install_libmariadb:
            # Install Python MariaDB connector
            install_mariadb, msg = await tools.add_python_package('mariadb')
            if install_mariadb:
                # If MariaDB connector installation is successful
                await send_response({
                    "action": "status",
                    "data": {
                        "category": "Database",
                        "name": "MariaDB",
                        "status": "installed",
                        "comment": "MariaDB connector has been installed successfully.",
                    }
                })
                return True
            else:
                # If MariaDB connector installation failed
                await send_response({
                    "action": "status",
                    "data": {
                        "category": "Database",
                        "name": "MariaDB",
                        "status": "error",
                        "comment": msg,
                    }
                })
                return False
        else:
            # If MariaDB dependency installation failed
            await send_response({
                "action": "status",
                "data": {
                    "category": "Database",
                    "name": "MariaDB",
                    "status": "error",
                    "comment": msg,
                }
            })
            return False
        

    else:
        # If already installed, bypass entire installation procedure
        return True
