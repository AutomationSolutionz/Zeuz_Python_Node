from Framework.install_handler.utils import check_package_available, install_package, send_response
import asyncio

async def check_status():
    """Checks whether any of psycopg or psycopg2 is installed."""

    print("[database][postgresql] Checking status...")
    is_psycopg_installed = await check_package_available("psycopg")
    is_psycopg2_installed = await check_package_available("psycopg2")

    if is_psycopg_installed or is_psycopg2_installed:
        psycopg_version = "psycopg" if is_psycopg_installed else "psycopg2"
        print(f"[database][postgresql] {psycopg_version} is installed.")
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
        print("[database][postgresql] psycopg is not installed.")
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
        install_psycopg = await install_package('psycopg')
        if install_psycopg:
            print("[database][postgresql] Installed successfully.")
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
                    "status": "not installed",
                    "comment": "There was an error installing the package.",
                }
            })
            return False

    else:
        return True


if __name__ == "__main__":
    asyncio.run(check_status())