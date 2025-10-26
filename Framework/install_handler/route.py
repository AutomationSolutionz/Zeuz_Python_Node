from pydantic import BaseModel, ConfigDict
from typing import Literal

services = [
    {
        "category": "Web",
        "services": [
            {
                "name": "Chrome For Testing",
                "status": "none",
                "comment": "Chrome for Testing is required to run web automation in Chrome browser",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": None,
                "install_function": None
            }
        ]
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
                "status_function": None,
                "install_function": None
            },
            {
                "name": "Node js 22",
                "status": "none",
                "comment": "Node js 22 is a tool for managing Node js 22 devices.",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": None,
                "install_function": None
            },
            {
                "name": "Appium",
                "status": "none",
                "comment": "Appium is a tool for managing Appium devices.",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": None,
                "install_function": None
            },
            {
                "name": "Java",
                "status": "none",
                "comment": "Java is a tool for managing Java devices.",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": None,
                "install_function": None
            },
            {
                "name": "Android Emulator",
                "status": "none",
                "comment": "Android Emulator is a tool for managing Android Emulator devices.",
                "install_text": "install",
                "os": ["windows", "linux", "darwin"],
                "status_function": None,
                "install_function": None
            }
        ]
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
                "status_function": None,
                "install_function": None
            }
        ]
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
                "status_function": None,
                "install_function": None
            }
        ]
    }
]


class Value(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    action: Literal["services_list", "install", "status"]
    data: dict | None = None

class Response(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    value: Value | None