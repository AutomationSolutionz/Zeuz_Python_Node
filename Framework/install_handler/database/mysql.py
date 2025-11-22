from Framework.install_handler.utils import send_response
from Framework.install_handler.installer_tools import InstallerTools

tools = InstallerTools()

async def check_status():
    """Checks if mysql-connector-python is installed."""

    if await tools.check_python_module_available("mysql.connector"):
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "MySQL",
                "status": "installed",
                "comment": "MySQL connector is installed.",
            }
        })
        return True
    else:
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "MySQL",
                "status": "not installed",
                "comment": "Install mysql-connector-python to connect to MySQL databases.",
            }
        })
        return False



async def install():
    is_already_installed = await check_status()

    if not is_already_installed:
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "MySQL",
                "status": "installing",
                "comment": "Downloading and installing, please wait...",
            }
        })
        install_mysql, msg = await tools.add_python_package('mysql-connector-python')

        if install_mysql:
            await send_response({
                "action": "status",
                "data": {
                    "category": "Database",
                    "name": "MySQL",
                    "status": "installed",
                    "comment": "MySQL connector has been installed successfully.",
                }
            })
            return True
        else:
            await send_response({
                "action": "status",
                "data": {
                    "category": "Database",
                    "name": "MySQL",
                    "status": "error",
                    "comment": msg,
                }
            })
            return False

    else:
        return True
