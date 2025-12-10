import datetime
import httpx
import platform
from Framework.Utilities import RequestFormatter, ConfigModule, CommonUtil

debug = False
version = "2.0.0"


def read_node_id():
    return CommonUtil.MachineInfo().getLocalUser().lower()


def generate_services_list(services):
    current_os = platform.system().lower()
    
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
        
        api_key = ConfigModule.get_config_value("Authentication", "api-key")
        url = RequestFormatter.form_uri("d/nodes/install/server/push")
        data['last_updated'] = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        data['version'] = version
        data['node_id'] = read_node_id()

        services_list = generate_services_list(services)
        #Lazy import to avoid circular dependency
        # android_emulator -> emulator -> utils (circular if imported at top level)
        try:
            from Framework.install_handler.android.emulator import get_filtered_avd_services
            avd_list = await get_filtered_avd_services()
            if avd_list:
                services_list.insert(1, avd_list)
        except Exception as e:
            if debug:
                print(f"[installer] Error getting AVD services: {e}")
        

        if data['action'] == "status":
            data['all_data'] = {
                "system_info": None,
                "services": services_list
            }
        
        if debug: 
            print(f"[installer] Sending response to server: {data}")
        
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            resp = await client.post(url, json=data, headers={"X-API-KEY": api_key})
            if debug: 
                print(f"[installer] Response status: {resp.status_code}")
                print(f"[installer] Response content: {resp.content}")
            if not resp.is_success:
                if debug: 
                    print(f"[installer] Failed to send response: {resp.status_code}")
    except Exception as e:
        print(f"[installer] Error sending response: {e}")
