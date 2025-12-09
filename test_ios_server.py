#!/usr/bin/env python3
"""
Simple test script to verify iOS endpoints work
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from server.mobile import get_ios_devices, inspect_ios

def test_ios_endpoints():
    print("Testing iOS endpoints...")
    
    # Test device listing
    print("\n1. Testing get_ios_devices():")
    devices = get_ios_devices()
    print(f"Found {len(devices)} devices:")
    for device in devices:
        print(f"  - {device.name} ({device.udid})")
    
    # Test screenshot capture
    print("\n2. Testing inspect_ios():")
    result = inspect_ios()
    print(f"Status: {result.status}")
    if result.error:
        print(f"Error: {result.error}")
    else:
        print(f"Screenshot length: {len(result.screenshot) if result.screenshot else 0} characters")
        print(f"XML available: {'Yes' if result.ui_xml else 'No'}")

if __name__ == "__main__":
    test_ios_endpoints()
