from Framework.install_handler.utils import check_package_available, install_package, send_response
import asyncio

async def check_status():
    """Checks if mysql-connector-python is installed."""

    print("[database][mysql] Checking status...")

    if await check_package_available("mysql.connector"):
        print(f"[database][MySQL] MySQL connector is installed.")
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
        print("[database][mysql] MySQL connector is not installed.")
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
        print("[database][mysql] Installing...")
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "MySQL",
                "status": "installing",
                "comment": "Downloading and installing, please wait...",
            }
        })
        install_mysql = await install_package('mysql-connector-python')
        if install_mysql:
            print("[database][mysql] Installed successfully.")
            await send_response({
                "action": "status",
                "data": {
                    "category": "Database",
                    "name": "MySQL",
                    "status": "installed",
                    "comment": "MySQL connector (mysql-connector-python) has been installed successfully.",
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
                    "comment": "There was an error installing the package. Please see the error log in Node terminal.",
                }
            })
            return False

    else:
        return True


if __name__ == "__main__":
    asyncio.run(check_status())