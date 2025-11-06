from pydantic import BaseModel, ConfigDict
from typing import Literal
import asyncio


from .web import chrome_for_testing
from .android import adb, node_js_22, appium, java, android_emulator, android_sdk, jdk, emulator,install_android_items
from .ios import xcode
from .database import postgresql, mysql, mariadb, oracle, install_db_items
from .windows import inspector
from .android.emulator import android_emulator_install


services = [
   {
       "category": "Web",
       "install_function": chrome_for_testing.install,

       "services": [
           {
               "name": "Chrome For Testing",
               "status": "none",
               "comment": "Chrome for Testing is required to run web automation in Chrome browser. ZZZ",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": chrome_for_testing.check_status,
               "install_function": chrome_for_testing.install
           }
       ]
   },
   {
        "category": "AndroidEmulator",
        "install_function": android_emulator_install,
        "installables": [],
        "services": [],
    },
    {
       "category": "Android",
       "install_function": install_android_items.install,
       "services": [
           {
               "name": "ADB",
               "status": "none",
               "comment": "ADB is a tool for managing Android devices.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": adb.check_status,
               "install_function": adb.install
           },
           {
               "name": "Node js 22",
               "status": "none",
               "comment": "Node js 22 is a tool for managing Node js 22 devices.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": node_js_22.check_status,
               "install_function": node_js_22.install
           },
           {
               "name": "Appium",
               "status": "none",
               "comment": "Appium is a tool for managing Appium devices.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": appium.check_status,
               "install_function": appium.install
           },
           {
               "name": "Java",
               "status": "none",
               "comment": "Java is a tool for managing Java devices.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": java.check_status,
               "install_function": java.install
           },
           {
               "name": "JDK",
               "status": "none",
               "comment": "JDK is a tool for managing JDK devices.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": jdk.check_status,
               "install_function": jdk.install
           },
           {
               "name": "Android SDK",
               "status": "none",
               "comment": "Android SDK is a tool for managing Android SDK devices.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": android_sdk.check_status,
               "install_function": android_sdk.install
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
               "status_function": xcode.check_status,
               "install_function": xcode.install
           }
       ]
   },
   {
       "category": "Database",
       "install_function": install_db_items.install,
       "services": [
           {
               "name": "PostgreSQL",
               "status": "none",
               "comment": "PostgreSQL driver is required to connect to PostgreSQL database.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": postgresql.check_status,
               "install_function": postgresql.install
           },
           {
               "name": "MySQL",
               "status": "none",
               "comment": "MySQL driver is required to connect to MySQL database.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": mysql.check_status,
               "install_function": mysql.install
           },
           {
               "name": "MariaDB",
               "status": "none",
               "comment": "MariaDB driver is required to connect to MariaDB database.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": mariadb.check_status,
               "install_function": mariadb.install
           },
           {
               "name": "Oracle",
               "status": "none",
               "comment": "Oracle driver is required to connect to Oracle database.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": oracle.check_status,
               "install_function": oracle.install
           }
       ]
   },
   {
       "category": "Windows",
       "install_function": inspector.install,
       "services": [
           {
               "name": "Inspector",
               "status": "none",
               "comment": "Inspector is a tool for managing Inspector devices.",
               "install_text": "install",
               "os": ["windows"],
               "status_function": inspector.check_status,
               "install_function": inspector.install
           }
       ]
   }
]



try:
    avds = asyncio.run(emulator.get_available_avds())
except RuntimeError:
    # Event loop already running, use a different approach
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, initialize empty and populate later
            avds = []
        else:
            avds = loop.run_until_complete(emulator.get_available_avds())
    except RuntimeError:
        avds = []

for category in services:
    if category["category"] == "AndroidEmulator":
        category["services"] = avds
        break


class Item(BaseModel):
   name: str | None = None
   category: str


class Value(BaseModel):
   model_config = ConfigDict(extra='forbid')
  
   action: Literal["services_list", "install", "status","install_category"]
   item: Item | None = None


class Response(BaseModel):
   model_config = ConfigDict(extra='forbid')
  
   value: Value | None

