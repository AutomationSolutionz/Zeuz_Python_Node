from Framework.install_handler.utils import check_package_available, install_package, send_response
import asyncio

async def check_status():
    """Checks if cx_Oracle Python library is installed."""

    print("[database][oracle] Checking status...")

    if await check_package_available("cx_Oracle"):
        print(f"[database][oracle] Oracle connector is installed.")
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "Oracle",
                "status": "installed",
                "comment": "Oracle connector (cx_Oracle) is installed.",
            }
        })
        return True
    else:
        print("[database][oracle] Oracle connector is not installed.")
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "Oracle",
                "status": "not installed",
                "comment": "Install cx_Oracle to connect to Oracle databases.",
            }
        })
        return False



async def install():
    is_already_installed = await check_status()

    if not is_already_installed:
        print("[database][oracle] Installing...")
        await send_response({
            "action": "status",
            "data": {
                "category": "Database",
                "name": "Oracle",
                "status": "installing",
                "comment": "Downloading and installing, please wait...",
            }
        })
        install_oracle, msg = await install_package('cx_Oracle') # NOTE: cx_Oracle is deprecated and gives install error
        if install_oracle:
            print("[database][oracle] Installed successfully.")
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


if __name__ == "__main__":
    asyncio.run(check_status())