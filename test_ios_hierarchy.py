#!/usr/bin/env python3
"""
Test script to check all available iOS hierarchy extraction methods
"""
import requests
import subprocess
import json

def test_webdriver_agent():
    """Test WebDriverAgent on common ports"""
    print("🧪 Testing WebDriverAgent...")
    ports = [8100, 8101, 8102]
    
    for port in ports:
        try:
            url = f"http://localhost:{port}"
            print(f"  Trying port {port}...")
            
            # Check status
            response = requests.get(f"{url}/status", timeout=2)
            if response.status_code == 200:
                print(f"  ✅ WebDriverAgent running on port {port}")
                
                # Check sessions
                sessions = requests.get(f"{url}/sessions", timeout=2)
                if sessions.status_code == 200:
                    session_data = sessions.json()
                    print(f"  Sessions: {len(session_data)}")
                    
                    if session_data:
                        session_id = session_data[0]['id']
                        source = requests.get(f"{url}/session/{session_id}/source", timeout=3)
                        if source.status_code == 200:
                            print(f"  ✅ Got XML hierarchy ({len(source.text)} chars)")
                            return source.text
                
                # Try direct source
                source = requests.get(f"{url}/source", timeout=2)
                if source.status_code == 200:
                    print(f"  ✅ Got XML hierarchy via direct source ({len(source.text)} chars)")
                    return source.text
                    
        except Exception as e:
            print(f"  ❌ Port {port}: {e}")
    
    print("  ❌ WebDriverAgent not found")
    return None

def test_appium_server():
    """Test Appium server"""
    print("\n🧪 Testing Appium Server...")
    try:
        response = requests.get("http://localhost:4723/status", timeout=2)
        if response.status_code == 200:
            print("  ✅ Appium server running on port 4723")
            return True
        else:
            print("  ❌ Appium server not responding")
    except Exception as e:
        print(f"  ❌ Appium server: {e}")
    return False

def test_xcrun_accessibility():
    """Test xcrun accessibility methods"""
    print("\n🧪 Testing xcrun accessibility methods...")
    
    # Get booted device
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "-j"],
            capture_output=True, text=True, check=True
        )
        devices_data = json.loads(result.stdout)
        booted_device = None
        
        for runtime, devices in devices_data.get("devices", {}).items():
            for device in devices:
                if device.get("state") == "Booted":
                    booted_device = device["udid"]
                    print(f"  Found booted device: {device['name']} ({booted_device})")
                    break
            if booted_device:
                break
        
        if not booted_device:
            print("  ❌ No booted iOS simulator found")
            return None
            
        # Try accessibility inspector
        print("  Trying accessibility methods...")
        
        # Method 1: Try to enable accessibility
        try:
            subprocess.run([
                "xcrun", "simctl", "spawn", booted_device, 
                "defaults", "write", "com.apple.Accessibility", "ApplicationAccessibilityEnabled", "-bool", "true"
            ], capture_output=True, timeout=5)
            print("  ✅ Accessibility enabled")
        except:
            print("  ⚠️  Could not enable accessibility")
        
        # Method 2: Try to get accessibility tree (this usually doesn't work without additional tools)
        print("  ❌ xcrun doesn't provide direct UI hierarchy access")
        
    except Exception as e:
        print(f"  ❌ xcrun accessibility: {e}")
    
    return None

def main():
    print("iOS UI Hierarchy Extraction Test")
    print("=" * 50)
    
    # Test all methods
    wda_xml = test_webdriver_agent()
    appium_available = test_appium_server()
    xcrun_result = test_xcrun_accessibility()
    
    print("\n📋 Summary:")
    print("=" * 50)
    
    if wda_xml:
        print("✅ RECOMMENDED: WebDriverAgent is working - use this for real hierarchy")
        # Save sample
        with open("sample_ios_hierarchy.xml", "w") as f:
            f.write(wda_xml)
        print("  Sample saved to: sample_ios_hierarchy.xml")
    else:
        print("❌ WebDriverAgent not available")
        print("\n🔧 To set up WebDriverAgent:")
        print("1. Clone: git clone https://github.com/appium/WebDriverAgent.git")
        print("2. Open WebDriverAgent.xcodeproj in Xcode")
        print("3. Select WebDriverAgentRunner scheme")
        print("4. Select your iOS Simulator as target")
        print("5. Build and Run (Cmd+R)")
        print("6. It will start on http://localhost:8100")
    
    if appium_available:
        print("✅ Appium server available - can be used as fallback")
        print("  Start iOS session to get hierarchy")
    else:
        print("❌ Appium server not available")
        print("  Install: npm install -g appium")
        print("  Start: appium server")
    
    print("\n🎯 Current Status:")
    if wda_xml:
        print("  Ready to use real iOS hierarchy!")
    elif appium_available:
        print("  Can use Appium for hierarchy")
    else:
        print("  No real hierarchy source available - will use fallback")

if __name__ == "__main__":
    main()
