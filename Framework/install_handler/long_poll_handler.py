import asyncio
import datetime
import traceback
import random
import platform
import httpx
import inspect
from colorama import Fore
from Framework.install_handler.route import Response, services, version
from Framework.install_handler.utils import send_response, debug, read_node_id
from pydantic import BaseModel
from Framework.Utilities import RequestFormatter, ConfigModule
from Framework.node_server_state import STATE
from Framework.install_handler.android.emulator import create_avd_from_system_image
from Framework.install_handler.system_info.system_info import get_formatted_system_info

if debug:
    print(f"[installer] Debug mode enabled")

class InstallHandler:

    def __init__(self):
        self.cancel_ = False
        self.running = False
        self.client = None

    async def on_message(self, message: Response) -> None:
        try:
            if debug: print(f"[installer] Received message:\n {message.model_dump_json(indent=4)}")
            if message.value is None:
                return
            now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            action = message.value.action
            if action == "services_list":
                current_os = platform.system().lower()
                if debug: print(f"[installer] Current OS: {current_os}")
                
                filtered_services = []
                for category in services:
                    filtered_category = {
                        "category": category["category"],
                        "services": []
                    }
                    for service in category["services"]:
                        if current_os not in service["os"]:
                            if debug: print(f"[installer] Skipping {service['name']} - not compatible with {current_os}")
                            continue
                        
                        filtered_service = {
                            "name": service["name"],
                            "status": service["status"],
                            "comment": service["comment"],
                            "install_text": service["install_text"],
                            "os": service["os"],
                            "user_password": service["user_password"]
                        }
                        filtered_category["services"].append(filtered_service)
                    
                    if filtered_category["services"]:
                        filtered_services.append(filtered_category)
                
                services_list = {
                    "timestamp": now,
                    "version": version,
                    "services": {
                        "system_info": None,
                        "categories": filtered_services
                    }
                }
                await send_response({
                    "action": "services_list",
                    "data": services_list
                })
            elif action == "system_info":
                if debug: print(f"[installer] Received system_info request")
                try:
                    # Get formatted system info
                    print("system info")
                    system_info_response = await get_formatted_system_info()
                    # Send the response to server
                    await send_response({
                        "timestamp": now,
                        "version": version,
                        "action": "system_info",
                        "data": system_info_response
                    })
                    if debug: print(f"[installer] System info sent successfully")
                except Exception as e:
                    print(f"[installer] Error getting/sending system info: {e}")
                    traceback.print_exc()
            elif action in ["install", "status"]:
                if debug: print(f"[installer] Installing {message}")

                # Extract user_password only for install actions (not for status)
                user_password = ""
                if action == "install" and message.value.item:
                    user_password = getattr(message.value.item, 'user_password', "") or ""

                category = [i for i in services if i["category"] == message.value.item.category][0]
                
                # Handle AndroidEmulator category
                if category["category"] == "AndroidEmulator":
                    service_name = message.value.item.name
                    
                    # Case 1: No service name or empty - get system images list
                    if not service_name or service_name is None or service_name.strip() == "":
                        if action == "install" and "install_function" in category and category["install_function"]:
                            func = category["install_function"]
                            await func()
                            return
                        else:
                            print(f"[installer] No install_function found for AndroidEmulator category")
                            return
                    
                    # Case 2: Service name is a system image (starts with "system-images;")
                    if service_name.startswith("system-images;"):
                        if action == "install":
                            await create_avd_from_system_image(service_name)
                            return
                        else:
                            print(f"[installer] Status check not supported for system images")
                            return
                    
                    # Case 3: Service name is an existing AVD - find it in services list
                    service = None
                    for s in category["services"]:
                        if s["name"] == service_name:
                            service = s
                            break
                    
                    if service:
                        if action == "install":
                            func = service.get("install_function")
                        elif action == "status":
                            func = service.get("status_function")
                        
                        if func is None:
                            print(f"[installer] Function not found for {service_name}")
                            return
                        await func()
                    else:
                        print(f"[installer] Service '{service_name}' not found in AndroidEmulator category")
                    return
                
                # Normal service-level install for other categories
                service = [i for i in category["services"] if i["name"] == message.value.item.name][0]
                if action == "install":
                    func = service["install_function"]
                    if func is None:
                        print(f"[installer] Function not found for {message.value.item.name}")
                        return
                    # Check if function accepts parameters
                    sig = inspect.signature(func)
                    if len(sig.parameters) > 0:
                        # Function accepts parameters, pass user_password
                        await func(user_password)
                    else:
                        # Function doesn't accept parameters, call without (backward compatibility)
                        await func()
                elif action == "status":
                    func = service["status_function"]
                    if func is None:
                        print(f"[installer] Function not found for {message.value.item.name}")
                        return
                    await func()

        except Exception as e:
            traceback.print_exc()

    async def cancel_run(self) -> None:
        self.cancel_ = True
        if self.running:
            if debug: print("[installer] Cancelling install listener...")
        else:
            if debug: print("[installer] Not running.")

    async def run(self) -> None:
        self.cancel_ = False
        if self.running:
            if debug: print("[installer] Already running.")
            return
        if debug: print(f"[installer] Started running")
        async with httpx.AsyncClient(timeout=httpx.Timeout(70.0), verify=False) as client:
            self.client = client
            while not self.cancel_:
                if STATE.reconnect_with_credentials is not None:
                    if debug: print("[installer] Reconnection requested, stopping...")
                    break
                
                self.running = True
                try:                
                    if debug: print("[installer] Active")
                    api_key = ConfigModule.get_config_value("Authentication", "api-key")
                    url = RequestFormatter.form_uri(f"d/nodes/install/node/listen?node_id={read_node_id()}")
                    
                    resp = await client.get(url, headers={"X-API-KEY": api_key})
                    if resp.status_code == httpx.codes.NO_CONTENT:
                        continue

                    if not resp.is_success:
                        if debug: 
                            print(
                                "[installer] facing difficulty communicating with the server, status code:",
                                resp.status_code,
                                " | reconnecting",
                            )
                            print(Fore.YELLOW + str(resp.content))

                        await asyncio.sleep(random.randint(1, 3))
                        continue

                    try:
                        data = resp.json()
                        if data:
                            validated_data = Response(**data)
                            await self.on_message(validated_data)
                    except Exception as e:
                        print(f"[installer] Error parsing response: {e}")
                        continue

                except httpx.ReadTimeout:
                    pass
                except httpx.ConnectError:
                    if debug: print("[installer] Connection error, retrying...")
                    await asyncio.sleep(random.randint(3, 5))
                except Exception:
                    if debug: traceback.print_exc()
                    if debug: print("[installer] RETRYING...")
                    await asyncio.sleep(random.randint(1, 3))

            self.running = False
            print("[installer] Stopped running")