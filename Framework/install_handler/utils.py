import httpx
from Framework.Utilities import RequestFormatter, ConfigModule, CommonUtil

debug = False

node_id = CommonUtil.MachineInfo().getLocalUser().lower()

async def send_response(data=None) -> None:
    try:
        api_key = ConfigModule.get_config_value("Authentication", "api-key")
        url = RequestFormatter.form_uri("d/nodes/install/server/push")
        payload = {
            "node_id": node_id,
            "data": data
        }
        if debug: 
            print(f"[installer] Sending response to server: {payload}")
        
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            resp = await client.post(url, json=payload, headers={"X-API-KEY": api_key})
            if debug: 
                print(f"[installer] Response status: {resp.status_code}")
                print(f"[installer] Response content: {resp.content}")
            if not resp.is_success:
                if debug: 
                    print(f"[installer] Failed to send response: {resp.status_code}")
    except Exception as e:
        print(f"[installer] Error sending response: {e}")

