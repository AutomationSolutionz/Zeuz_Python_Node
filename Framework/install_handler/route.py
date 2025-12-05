from pydantic import BaseModel, ConfigDict
from typing import Literal
import asyncio


from .web import chrome_for_testing, edge, mozilla
from .android import adb, node_js_22, appium, java, android_emulator, android_sdk, jdk, emulator
from .ios import xcode
from .database import postgresql, mysql, mariadb, oracle
from .windows import inspector
from .android.emulator import android_emulator_install


services = [
   {
       "category": "Web",

       "services": [
           {
               "name": "Chrome For Testing",
               "status": "none",
               "comment": "Chrome for Testing is required to run web automation in Chrome browser.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": chrome_for_testing.check_status,
               "install_function": chrome_for_testing.install,
               "user_password": "no",
           },
           {
               "name": "Mozilla",
               "status": "none",
               "comment": "Mozilla Firefox is required to run web automation in Mozilla Firefox browser.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": mozilla.check_status,
               "install_function": mozilla.install,
               "user_password": "yes",
           },
           {
               "name": "Edge",
               "status": "none",
               "comment": "Microsoft Edge is required to run web automation in Microsoft Edge browser.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": edge.check_status,
               "install_function": edge.install,
               "user_password": "yes",
           }
           
       ]
   },
   {
        "category": "AndroidEmulator",
        "name" : "System Images",
        "install_text": "install",
        "install_function": android_emulator_install,
        "installables": [],
        "services": [],
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
               "user_password": "no",
           },
           {
               "name": "Node js 22",
               "status": "none",
               "comment": "Node js 22 is a tool for managing Node js 22 devices.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": node_js_22.check_status,
               "install_function": node_js_22.check_status, #on purpose. Node 22 is installed when node starts.
               "user_password": "no",
           },
           {
               "name": "Appium",
               "status": "none",
               "comment": "Appium is a tool for managing Appium devices.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": appium.check_status,
               "install_function": appium.check_status, #on purpose. Appium is installed when node starts.
               "user_password": "no",
           },
           {
               "name": "Java",
               "status": "none",
               "comment": "Java is a tool for managing Java devices.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": java.check_status,
               "install_function": java.install, #install jdk here also. jdk.install will install java also.
               "user_password": "no"
           },
           {
               "name": "JDK",
               "status": "none",
               "comment": "JDK is a tool for managing JDK devices.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": jdk.check_status,
               "install_function": jdk.install,
              "user_password": "no"
           },
           {
               "name": "Android SDK",
               "status": "none",
               "comment": "Android SDK is a tool for managing Android SDK devices.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": android_sdk.check_status,
               "install_function": android_sdk.install,
               "user_password": "no"
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
               "install_function": xcode.install,
               "user_password": "no"
           }
       ]
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
               "user_password": "no"
           },
           {
               "name": "MySQL",
               "status": "none",
               "comment": "MySQL driver is required to connect to MySQL database.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": mysql.check_status,
               "install_function": mysql.install,
               "user_password": "no"
           },
           {
               "name": "MariaDB",
               "status": "none",
               "comment": "MariaDB driver is required to connect to MariaDB database.",
               "install_text": "install",
               "os": ["windows", "linux", "darwin"],
               "status_function": mariadb.check_status,
               "install_function": mariadb.install,
               "user_password": "yes"
           },
           {
               "name": "Oracle",
               "status": "none",
               "comment": "Oracle driver is required to connect to Oracle database.",
               "install_text": "install",
                "os": ["windows", "linux", "darwin"],
               "status_function": oracle.check_status,
               "install_function": oracle.install,
               "user_password": "no"
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
               "install_function": inspector.install,
               "user_password": "no"
           }
       ]
   }
]



# try:
#     avds = asyncio.run(emulator.get_available_avds())
# except RuntimeError:
#     # Event loop already running, use a different approach
#     try:
#         loop = asyncio.get_event_loop()
#         if loop.is_running():
#             # If loop is running, initialize empty and populate later
#             avds = []
#         else:
#             avds = loop.run_until_complete(emulator.get_available_avds())
#     except RuntimeError:
#         avds = []

# def _populate_avds():
#     """Populate the AndroidEmulator category with available AVDs"""
#     try:
#         loop = asyncio.get_event_loop()
#         if loop.is_running():
#             # If loop is running, we need to schedule it
#             async def refresh():
#                 avds = await emulator.get_available_avds()
#                 for category in services:
#                     if category["category"] == "AndroidEmulator":
#                         category["services"] = avds
#                         break
#             # Schedule the refresh
#             asyncio.create_task(refresh())
#         else:
#             avds = loop.run_until_complete(emulator.get_available_avds())
#             for category in services:
#                 if category["category"] == "AndroidEmulator":
#                     category["services"] = avds
#                     break
#     except Exception as e:
#         print(f"[installer][route] Error refreshing AVD list: {e}")


# async def refresh_avd_list():
#     """Refresh the AVD list in the AndroidEmulator category"""
#     try:
#         avds = await emulator.get_available_avds()
#         for category in services:
#             if category["category"] == "AndroidEmulator":
#                 category["services"] = avds
#                 break
#         print(f"[installer][route] Refreshed AVD list: {len(avds)} AVDs found")
#     except Exception as e:
#         print(f"[installer][route] Error refreshing AVD list: {e}")


# for category in services:
#     if category["category"] == "AndroidEmulator":
#         category["services"] = avds
#         break


class Item(BaseModel):
   name: str | None = None
   category: str
   user_password: str = ""  # Optional user password for installations requiring sudo/admin


class Value(BaseModel):
   model_config = ConfigDict(extra='forbid')
  
   action: Literal["services_list", "install", "status", "install_category", "system_info"]
   item: Item | None = None


class Response(BaseModel):
   model_config = ConfigDict(extra='forbid')
  
   value: Value | None