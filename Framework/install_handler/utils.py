import datetime
import asyncio
import platform
from Framework.Utilities import RequestFormatter, ConfigModule, CommonUtil

debug = False
version = "2.0.0"
current_os = platform.system().lower()


def read_node_id():
    return CommonUtil.MachineInfo().getLocalUser().lower()


def generate_services_list(services):
    filtered_services = []
    for category in services:
        filtered_category = {
            "group": category["group"],
            "category": category["category"],
            "services": []
        }
        for service in category["services"]:
            if current_os not in service["os"]:
                continue
            
            filtered_service = {
                "name": service["name"],
                "status": service["status"],
                "comment": service["comment"],
                "install_text": service["install_text"],
                "check_text": service["check_text"],
                "user_password": service["user_password"]
            }
            filtered_category["services"].append(filtered_service)
        
        filtered_services.append(filtered_category)
    
    return filtered_services


async def send_response(data=None) -> None:
    try:
        from Framework.install_handler.route import services
        host = RequestFormatter.form_uri("d/nodes/install/server/push")
        data['last_updated'] = datetime.datetime.now(datetime.timezone.utc).timestamp()
        data['version'] = version
        data['node_id'] = read_node_id()

        services_list = generate_services_list(services)

        if data['action'] in ["status", "group_status", "services_update"]:
            data['all_data'] = {
                "system_info": None,
                "services": services_list
            }
        
        if debug: 
            print(f"[installer] Sending response to server: {data}")
        
        for _ in range(3):
            try:
                resp = RequestFormatter.request("post", host, json=data, timeout=70)
                if debug: 
                    print(f"[installer] Response status: {resp.status_code}")
                    print(f"[installer] Response content: {resp.content}")
                if not resp.ok:
                    if debug: 
                        print(f"[installer] Failed to send response: {resp.status_code}")
                    await asyncio.sleep(3,5)
                else:
                    break
            except Exception as e:
                if debug: print(e)
                await asyncio.sleep(3,5)
    except Exception as e:
        print(f"[installer] Error sending response: {e}")
