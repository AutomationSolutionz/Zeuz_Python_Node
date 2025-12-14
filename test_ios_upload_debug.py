#!/usr/bin/env python3
import sys
import os
import requests
import hashlib
sys.path.append(os.path.dirname(__file__))

from server.mobile import get_ios_devices, capture_ios_ui_dump, IOS_XML_PATH
from Framework.Utilities import ConfigModule, CommonUtil

def test_upload_once():
    print("Testing iOS XML upload once...")
    
    try:
        # Get device
        ios_devices = get_ios_devices()
        if not ios_devices:
            print("❌ No iOS devices found")
            return
        
        device_udid = ios_devices[0].udid
        print(f"✅ Using device: {device_udid}")
        
        # Capture XML
        capture_ios_ui_dump(device_udid)
        print("✅ XML captured")
        
        # Read XML
        with open(IOS_XML_PATH, 'r', encoding='utf-8') as xml_file:
            xml_content = xml_file.read()
        
        print(f"✅ XML length: {len(xml_content)} chars")
        
        # Get config
        server_address = ConfigModule.get_config_value("Authentication", "server_address").strip()
        api_key = ConfigModule.get_config_value("Authentication", "api-key").strip()
        node_id = CommonUtil.MachineInfo().getLocalUser().lower()
        
        print(f"✅ Server: {server_address}")
        print(f"✅ Node ID: {node_id}")
        
        # Upload
        url = server_address + "/node_ai_contents/"
        payload = {
            "dom_mob": {"dom": xml_content},
            "node_id": node_id
        }
        
        print(f"📤 Uploading to: {url}")
        
        response = requests.post(
            url,
            headers={"X-Api-Key": api_key},
            json=payload,
            timeout=10
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response: {response.text[:200]}...")
        
        if response.ok:
            print("✅ Upload successful!")
        else:
            print("❌ Upload failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_upload_once()
