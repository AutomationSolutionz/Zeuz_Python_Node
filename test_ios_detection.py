import subprocess
import json
import sys

def test_xcrun_availability():
    """Test if xcrun command is available"""
    try:
        result = subprocess.run(["xcrun", "--version"], capture_output=True, text=True, check=True)
        print("xcrun is available")
        print(f"Version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print("xcrun is not available")
        print(f"Error: {e}")
        return False

def test_simctl_list():
    """Test if simctl list devices works"""
    try:
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "-j"],
            capture_output=True, text=True, check=True
        )
        print("simctl list devices works")
        
        devices_data = json.loads(result.stdout)
        print(f"Found {len(devices_data.get('devices', {}))} runtime categories")
        
        total_devices = 0
        available_devices = 0
        
        for runtime, devices in devices_data.get("devices", {}).items():
            runtime_available = 0
            for device in devices:
                total_devices += 1
                if device.get("isAvailable", False):
                    available_devices += 1
                    runtime_available += 1
            
            if runtime_available > 0:
                print(f"  {runtime}: {runtime_available} available devices")
        
        print(f"Total devices: {total_devices}")
        print(f"Available devices: {available_devices}")
        
        return available_devices > 0
        
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        print("simctl list devices failed")
        print(f"Error: {e}")
        return False

def test_screenshot_capability():
    """Test if we can take a screenshot from the first available device"""
    try:
        # Get available devices
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "-j"],
            capture_output=True, text=True, check=True
        )
        
        devices_data = json.loads(result.stdout)
        first_device = None
        
        for runtime, devices in devices_data.get("devices", {}).items():
            for device in devices:
                if device.get("isAvailable", False) and device.get("state") == "Booted":
                    first_device = device
                    break
            if first_device:
                break
        
        if not first_device:
            print("No booted iOS simulators found. Please start an iOS simulator first.")
            return False
        
        print(f"Testing screenshot with device: {first_device['name']} ({first_device['udid']})")
        
        # Try to take a screenshot
        result = subprocess.run(
            ["xcrun", "simctl", "io", first_device["udid"], "screenshot", "test_screenshot.png"],
            capture_output=True, text=True, check=True
        )
        
        print("Screenshot capability works")
        print("Screenshot saved as test_screenshot.png")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        print("Screenshot test failed")
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing iOS Device Detection and Screenshot Capability")
    print("=" * 60)
    
    tests = [
        ("xcrun availability", test_xcrun_availability),
        ("simctl device listing", test_simctl_list),
        ("screenshot capability", test_screenshot_capability),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! iOS device detection should work.")
        return 0
    else:
        print("Some tests failed. Please check the requirements.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
