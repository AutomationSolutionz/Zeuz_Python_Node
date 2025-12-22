from Framework.install_handler.utils import send_response
from Framework.install_handler.installer_tools import InstallerTools

tools = InstallerTools()

async def check_status():
    """Checks if oracledb Python library is installed."""

    if await tools.check_python_module_available("oracledb"):
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "Oracle",
                "status": "installed",
                "comment": "Oracle connector is installed.",
            }
        })
        return True
    else:
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "Oracle",
                "status": "not installed",
                "comment": "Install oracledb to connect to Oracle databases.",
            }
        })
        return False



async def install():
    is_already_installed = await check_status()

    if not is_already_installed:

        module_name = 'oracledb'

        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "Oracle",
                "status": "installing",
                "comment": "Downloading and installing, please wait...",
            }
        })

        # NOTE: cx_Oracle is deprecated and gives install error on Windows
        if module_name == "cx_Oracle":
            tools.logger.warning("cx_Oracle is deprecated, recommended to use oracledb instead.")

        install_oracle, msg = await tools.add_python_package(module_name) 
        if install_oracle:
            await send_response({
                "action": "status",
                "data": {
                    "category": "Database",
                    "name": "Oracle",
                    "status": "installed",
                    "comment": "Oracle connector has been installed successfully.",
                }
            })
            return True
        else:
            await send_response({
                "action": "status",
                "data": {
                    "category": "Database",
                    "name": "Oracle",
                    "status": "error",
                    "comment": msg,
                }
            })
            return False

    else:
        return True
