from pydantic import BaseModel, ConfigDict
from typing import Literal

from .web import chrome_for_testing
from .android import adb, node_js_22, appium, java, android_emulator
from .ios import xcode
from .database import postgresql, mysql, mariadb, oracle
from .windows import inspector
from .linux import atspi, xwd

services = [
    {
        "category": "Web",
        "services": [
            {
                "name": "Chrome For Testing",
                "status": "none",
                "comment": "Chrome for Testing is required to run web automation in Chrome browser. ZZZ",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": chrome_for_testing.check_status,
                "install_function": chrome_for_testing.install,
            }
        ],
    },
    {
        "category": "Android",
        "services": [
            {
                "name": "ADB",
                "status": "none",
                "comment": "ADB is a tool for managing Android devices.",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": adb.check_status,
                "install_function": adb.install,
            },
            {
                "name": "Node js 22",
                "status": "none",
                "comment": "Node js 22 is a tool for managing Node js 22 devices.",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": node_js_22.check_status,
                "install_function": node_js_22.install,
            },
            {
                "name": "Appium",
                "status": "none",
                "comment": "Appium is a tool for managing Appium devices.",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": appium.check_status,
                "install_function": appium.install,
            },
            {
                "name": "Java",
                "status": "none",
                "comment": "Java is a tool for managing Java devices.",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": java.check_status,
                "install_function": java.install,
            },
            {
                "name": "Android Emulator",
                "status": "none",
                "comment": "Android Emulator is a tool for managing Android Emulator devices.",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": android_emulator.check_status,
                "install_function": android_emulator.install,
            },
        ],
    },
    {
        "category": "iOS",
        "services": [
            {
                "name": "Xcode",
                "status": "none",
                "comment": "Xcode is a tool for managing Xcode devices.",
                "install_text": "install",
                "os": ["darwin"],
                "status_function": xcode.check_status,
                "install_function": xcode.install,
                "user_password": "yes",
            }
        ],
    },
    {
        "category": "MacOS",
        "services": [
            {
                "name": "Xcode",
                "status": "none",
                "comment": "Xcode is a tool for managing Xcode devices.",
                "install_text": "install",
                "os": ["darwin"],
                "status_function": xcode.check_status,
                "install_function": xcode.install,
                "user_password": "yes",
            }
        ],
    },
    {
        "category": "Database",
        "services": [
            {
                "name": "PostgreSQL",
                "status": "none",
                "comment": "PostgreSQL driver is required to connect to PostgreSQL database.",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": postgresql.check_status,
                "install_function": postgresql.install,
            },
            {
                "name": "MySQL",
                "status": "none",
                "comment": "MySQL driver is required to connect to MySQL database.",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": mysql.check_status,
                "install_function": mysql.install,
            },
            {
                "name": "MariaDB",
                "status": "none",
                "comment": "MariaDB driver is required to connect to MariaDB database.",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": mariadb.check_status,
                "install_function": mariadb.install,
            },
            {
                "name": "Oracle",
                "status": "none",
                "comment": "Oracle driver is required to connect to Oracle database.",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": oracle.check_status,
                "install_function": oracle.install,
            },
        ],
    },
    {
        "category": "Windows",
        "services": [
            {
                "name": "Inspector",
                "status": "none",
                "comment": "Inspector is a tool for managing Inspector devices.",
                "install_text": "install",
                "os": ["windows"],
                "status_function": inspector.check_status,
                "install_function": inspector.install,
            }
        ],
    },
    {
        "category": "Linux",
        "services": [
            {
                "name": "AT-SPI Packages",
                "status": "none",
                "comment": "AT-SPI development packages for Linux accessibility automation.",
                "install_text": "install",
                "os": ["linux"],
                "status_function": atspi.check_status,
                "install_function": atspi.install,
                "user_password": "yes",
            },
            {
                "name": "Screen Capture Utilities",
                "status": "none",
                "comment": "Screen Capture Utilities including xwd, imagemagick, and wmctrl.",
                "install_text": "install",
                "os": ["linux"],
                "status_function": xwd.check_status,
                "install_function": xwd.install,
                "user_password": "yes",
            },
        ],
    },
]


class Item(BaseModel):
    name: str
    category: str


class Value(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["services_list", "install", "status"]
    item: Item | None = None


class Response(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: Value | None
