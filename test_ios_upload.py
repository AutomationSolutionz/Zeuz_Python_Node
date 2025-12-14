#!/usr/bin/env python3
"""
Test script to start iOS XML upload to server
"""
import sys
import os
import asyncio
sys.path.append(os.path.dirname(__file__))

from server.mobile import upload_ios_ui_dump

async def main():
    print("Starting iOS XML upload to server...")
    print("This will continuously capture and upload iOS hierarchy")
    print("Press Ctrl+C to stop")
    
    try:
        await upload_ios_ui_dump()
    except KeyboardInterrupt:
        print("\nStopped iOS XML upload")

if __name__ == "__main__":
    asyncio.run(main())
