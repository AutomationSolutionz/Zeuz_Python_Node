from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional

from .web import chrome_for_testing, edge, mozilla
from .android import (
    adb,
    node_js_22,
    appium,
    java,
    android_sdk,
)
from .ios import xcode, simulator
from .macos import xcode as macos_xcode
from .windows import inspector
from .android import emulator

services = [
    {
        "group": {
            "check_text": "Check all",
            "install_text": "Install all",
        },
        "category": "Android",
        "services": [
            {
                "name": "Node js 22",
                "status": "none",
                "comment": "Node js 22 is a tool for managing Node js 22 devices.",
                "check_text":"Check status",
                "install_text": "Install",
                "os": ["windows", "linux", "darwin"],
                "status_function": node_js_22.check_status,
                "install_function": node_js_22.check_status,  # on purpose. Node 22 is installed when node starts.
                "user_password": False,
            },
            {
                "name": "Appium",
                "status": "none",
                "comment": "Appium is a tool for managing Appium devices.",
                "check_text":"Check status",
                "install_text": "Install",
                "os": ["windows", "linux", "darwin"],
                "status_function": appium.check_status,
                "install_function": appium.check_status,  # on purpose. Appium is installed when node starts.
                "user_password": False,
            },
            {
                "name": "Java",
                "status": "none",
                "comment": "Java is a tool for managing Java devices.",
                "check_text":"Check status",
                "install_text": "Install",
                "os": ["windows", "linux", "darwin"],
                "status_function": java.check_status,
                "install_function": java.install,  # install jdk here also. jdk.install will install java also.
                "user_password": False,
            },
            {
                "name": "Android SDK",
                "status": "none",
                "comment": "Android SDK is a tool for managing Android SDK devices.",
                "check_text":"Check status",
                "install_text": "Install",
                "os": ["windows", "linux", "darwin"],
                "status_function": android_sdk.check_status,
                "install_function": android_sdk.install,
                "user_password": False,
            },
            {
                "name": "ADB",
                "status": "none",
                "comment": "ADB is a tool for managing Android devices.",
                "check_text":"Check status",
                "install_text": "",
                "os": ["windows", "linux", "darwin"],
                "status_function": adb.check_status,
                "install_function": adb.install,
                "user_password": False,
            },
        ],
    },
    {
        "group": {
            "check_text": "Check all",
            "install_text": "",
        },
        "category": "AndroidEmulator",
        "name": "System Images",
        "check_text":"Check status",
        "install_text": "Install",
        "os": ["windows", "linux", "darwin"],
        "status_function": emulator.check_emulator_list,
        "install_function": emulator.android_emulator_install,
        "installables": [],
        "services": [],
    },
    {
        "category": "iOS",
        "group": {
            "check_text": "Check all",
            "install_text": "",
        },
        "services": [
            {
                "name": "Xcode",
                "status": "none",
                "comment": "Xcode is a tool for managing Xcode devices.",
                "check_text":"Check status",
                "install_text": "Install",
                "os": ["darwin"],
                "status_function": xcode.check_status,
                "install_function": xcode.install,
                "user_password": "yes",
            },
            {
                "name": "Simulator",
                "status": "none",
                "comment": "Simulator is a tool for managing Simulator devices.",
                "check_text":"Check status",
                "install_text": "Install",
                "os": ["darwin"],
                "status_function": simulator.check_status,
                "install_function": simulator.install,
                "user_password": "yes",
            },
        ],
    },
    {
        "group": {
            "check_text": "Check all",
            "install_text": "",
        },
        "category": "iOSSimulator",
        "name": "Device Types",
        "check_text":"Check status",
        "install_text": "Install",
        "os": ["darwin"],
        "status_function": simulator.check_simulator_list,
        "install_function": simulator.ios_simulator_install,
        "installables": [],
        "services": [],
    },
    {
        "category": "Web",
        "group": {
            "check_text": "Check all",
            "install_text": "Install all",
        },
        "services": [
            {
                "name": "Chrome For Testing",
                "status": "none",
                "comment": "Chrome for Testing is required to run web automation in Chrome browser.",
                "check_text":"Check status",
                "install_text": "Install",
                "os": ["windows", "linux", "darwin"],
                "status_function": chrome_for_testing.check_status,
                "install_function": chrome_for_testing.install,
                "user_password": False,
            },
            {
                "name": "Mozilla",
                "status": "none",
                "comment": "Mozilla Firefox is required to run web automation in Mozilla Firefox browser.",
                "check_text":"Check status",
                "install_text": "Install",
                "os": ["windows", "linux", "darwin"],
                "status_function": mozilla.check_status,
                "install_function": mozilla.install,
                "user_password": False,
            },
            {
                "name": "Edge",
                "status": "none",
                "comment": "Microsoft Edge is required to run web automation in Microsoft Edge browser.",
                "check_text":"Check status",
                "install_text": "Install",
                "os": ["windows", "linux", "darwin"],
                "status_function": edge.check_status,
                "install_function": edge.install,
                "user_password": "yes",
            },
        ],
    },
    {
        "category": "MacOS",
        "group": {
            "check_text": "Check all",
            "install_text": "",
        },
        "services": [
            {
                "name": "Xcode",
                "status": "none",
                "comment": "Xcode is a tool for managing Xcode devices.",
                "check_text":"Check status",
                "install_text": "Install",
                "os": ["darwin"],
                "status_function": macos_xcode.check_status,
                "install_function": macos_xcode.install,
                "user_password": "yes",
            }
        ],
    },
    {
        "category": "Windows",
        "group": {
            "check_text": "Check all",
            "install_text": "Install all",
        },
        "install_function": inspector.install,
        "services": [
            {
                "name": "Inspector",
                "status": "none",
                "comment": "Inspector is a tool for managing Inspector devices.",
                "check_text":"Check status",
                "install_text": "Install",
                "os": ["windows"],
                "status_function": inspector.check_status,
                "install_function": inspector.install,
                "user_password": "no",
            }
        ],
    },
]


class Item(BaseModel):
    name: Optional[str] = None
    category: str
    user_password: str = (
        ""  # Optional user password for installations requiring sudo/admin
    )


class Value(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal[
        "services_list",
        "install",
        "status",
        "system_info",
        "group_status",
        "group_install",
    ]
    item: Item | None = None


class Response(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: Value | None
