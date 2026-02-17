import httpx
import asyncio
from pathlib import Path
from Framework.install_handler.utils import send_response

inspector_path = Path("Apps/Windows/inspector.exe").absolute()
async def check_status() -> bool:
    print("[installer][windows-inspector] Checking status...")
    exists = inspector_path.exists()
    if exists:
        print("[installer][windows-inspector] Already installed")
        await send_response({
            "action": "status",
            "data": {
                "category": "Windows",
                "name": "Inspector",
                "status": "installed",
                "comment": f"Open the inspector here: {inspector_path}",
                "install_text": "installed",
            }
        })
        return True
    else:
        print("[installer][windows-inspector] Not installed")
        await send_response({
            "action": "status",
            "data": {
                "category": "Windows",
                "name": "Inspector",
                "status": "not installed",
                "comment": f"Install the inspector to use it.",
                "install_text": "install",
            }
        })
        return False


async def install() -> bool:
    print("[installer][windows-inspector] Installing...")
    
    status = inspector_path.exists()
    if status:
        await send_response({
            "action": "status",
            "data": {
                "category": "Windows",
                "name": "Inspector",
                "status": "installed",
                "comment": f"Open the inspector here: {inspector_path}",
                "install_text": "installed",
            }
        })
        print("[installer][windows-inspector] Already installed")
        return True
    
    url = "https://raw.githubusercontent.com/AutomationSolutionz/Zeuz_Python_Node_Setup/master/installation_files/Windows/inspector.exe"
    
    inspector_path.parent.mkdir(parents=True, exist_ok=True)
    
    async with httpx.AsyncClient(timeout=900.0) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            
            total_size = int(response.headers.get("content-length", 0))
            chunk_size = 8192
            downloaded = 0
            
            count = []
            with open(inspector_path, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        bar_length = 50
                        filled_length = int(bar_length * downloaded // total_size)
                        bar = '█' * filled_length + '-' * (bar_length - filled_length)
                        
                        mb_downloaded = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        
                        print(f"\r[installer][windows-inspector] |{bar}| {progress:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='', flush=True)

                        p = round(mb_downloaded/mb_total, 1)
                        if p not in count:
                            count.append(p)
                            asyncio.create_task(send_response({
                                "action": "status",
                                "data": {
                                    "category": "Windows",
                                    "name": "Inspector",
                                    "status": "installing",
                                    "comment": f"Downloading inspector... {progress:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)",
                                    "install_text": "installing",
                                }
                            }))
            
            print()
            print(f"[installer][windows-inspector] Download completed: {inspector_path}")
            print(f"[installer][windows-inspector] Installation successful")
            await send_response({
                "action": "status",
                "data": {
                    "category": "Windows",
                    "name": "Inspector",
                    "status": "installed",
                    "comment": f"Open the inspector here: {inspector_path}",
                    "install_text": "installed",
                }
            })
            return True
