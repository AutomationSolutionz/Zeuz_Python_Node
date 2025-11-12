from Framework.install_handler.utils import check_package_available, install_package, send_response
import asyncio

async def check_status():
    """Checks if mariadb Python library is installed."""

    print("[database][mariadb] Checking status...")

    if await check_package_available("mariadb"):
        print(f"[database][MariaDB] MariaDB connector is installed.")
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
        print("[database][mariadb] MariaDB connector is not installed.")
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



async def install():
    is_already_installed = await check_status()

    if not is_already_installed:
        print("[database][mariadb] Installing...")
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "MariaDB",
                "status": "installing",
                "comment": "Downloading and installing, please wait...",
            }
        })
        install_mariadb = await install_package('mariadb')
        if install_mariadb:
            print("[database][mariadb] Installed successfully")
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
            await send_response({
                "action": "status",
                "data": {
                    "category": "Database",
                    "name": "MariaDB",
                    "status": "not installed",
                    "comment": "There was an error installing the package.",
                }
            })
            return False

    else:
        return True


if __name__ == "__main__":
    asyncio.run(check_status())