from Framework.install_handler.utils import send_response
from Framework.install_handler.installer_tools import InstallerTools

tools = InstallerTools()

async def check_status():
    """Checks whether any of psycopg or psycopg2 is installed."""

    is_psycopg_installed = await tools.check_python_module_available("psycopg")
    is_psycopg2_installed = await tools.check_python_module_available("psycopg2")

    if is_psycopg_installed or is_psycopg2_installed:
        psycopg_version = "psycopg" if is_psycopg_installed else "psycopg2"
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "PostgreSQL",
                "status": "installed",
                "comment": f"PostgreSQL connector ({psycopg_version}) is installed.",
            }
        })
        return True
    else:
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "PostgreSQL",
                "status": "not installed",
                "comment": "Install psycopg to connect to PostgreSQL databases.",
            }
        })
        return False



async def install():
    is_already_installed = await check_status()

    if not is_already_installed:
        print("[database][postgresql] Installing...")
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "PostgreSQL",
                "status": "installing",
                "comment": "Downloading and installing, please wait...",
            }
        })
        install_psycopg, msg = await tools.add_python_package('psycopg')
        if install_psycopg:
            await send_response({
                "action": "status",
                "data": {
                    "category": "Database",
                    "name": "PostgreSQL",
                    "status": "installed",
                    "comment": "PostgreSQL connector (psycopg) has been installed successfully.",
                }
            })
            return True
        else:
            await send_response({
                "action": "status",
                "data": {
                    "category": "Database",
                    "name": "PostgreSQL",
                    "status": "error",
                    "comment": msg,
                }
            })
            return False

    else:
        return True
