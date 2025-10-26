import asyncio
import json
import traceback
import random
import platform
import httpx
from colorama import Fore
from Framework.install_handler.route import Response, services
from Framework.install_handler.utils import send_response, debug, node_id
from pydantic import BaseModel
from Framework.Utilities import RequestFormatter, ConfigModule

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
                            "os": service["os"]
                        }
                        filtered_category["services"].append(filtered_service)
                    
                    if filtered_category["services"]:
                        filtered_services.append(filtered_category)
                
                await send_response({
                    "action": "services_list",
                    "data": filtered_services
                })
            elif action in ["install", "status"]:
                if debug: print(f"[installer] Installing {message}")

                category = [i for i in services if i["category"] == message.value.item.category][0]
                service = [i for i in category["services"] if i["name"] == message.value.item.name][0]
                if action == "install":
                    func = service["install_function"]
                elif action == "status":
                    func = service["status_function"]
                
                if func is None:
                    print(f"[installer] Function not found for {message.value.item.name}")
                    return
                await func()

        except Exception as e:
            print(f"[installer] Error onMessage: {e}")
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
                from Framework.node_server_state import STATE
                if STATE.reconnect_with_credentials is not None:
                    if debug: print("[installer] Reconnection requested, stopping...")
                    break
                
                self.running = True
                try:                
                    if debug: print("[installer] Active")
                    api_key = ConfigModule.get_config_value("Authentication", "api-key")
                    url = RequestFormatter.form_uri(f"d/nodes/install/node/listen?node_id={node_id}")
                    
                    resp = await client.get(url, headers={"X-API-KEY": api_key})
                    if resp.status_code == httpx.codes.NO_CONTENT:
                        continue

                    if not resp.is_success:
                        print(
                            "[installer] facing difficulty communicating with the server, status code:",
                            resp.status_code,
                            " | reconnecting",
                        )
                        try:
                            print(Fore.YELLOW + str(resp.content))
                        except Exception:
                            pass

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
                    print("[installer] Connection error, retrying...")
                    await asyncio.sleep(random.randint(3, 5))
                except Exception:
                    traceback.print_exc()
                    print("[installer] RETRYING...")
                    await asyncio.sleep(random.randint(1, 3))

            self.running = False
            print("[installer] Stopped running")
