import asyncio
import sys

from Framework.install_handler.install_log_config import get_logger
from Framework.install_handler.utils import send_response


logger = get_logger()
NAME = "Playwright Firefox and WebKit"


async def _run(*args):
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "playwright",
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return process.returncode, (stdout + stderr).decode(errors="replace")


async def _status(installed, comment):
    await send_response(
        {
            "action": "status",
            "data": {
                "category": "Web",
                "name": NAME,
                "status": "installed" if installed else "not installed",
                "comment": comment,
            },
        }
    )


async def check_status():
    code, output = await _run("install", "--list")
    installed = (
        code == 0 and "firefox-" in output.lower() and "webkit-" in output.lower()
    )
    await _status(
        installed,
        "Bundled Firefox and WebKit are installed."
        if installed
        else "Install Playwright Firefox and WebKit to use those engines.",
    )
    return installed


async def install():
    logger.info("[installer][web-playwright] Installing Firefox and WebKit...")
    code, output = await _run("install", "firefox", "webkit")
    if code:
        logger.error("[installer][web-playwright] %s", output)
        await _status(False, "Failed to install Playwright Firefox and WebKit.")
        return False
    await _status(True, "Bundled Firefox and WebKit are installed.")
    return True
