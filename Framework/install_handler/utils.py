import datetime
import asyncio
import os
import re
import platform
from typing import Callable, Awaitable
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
                resp = await RequestFormatter.request("post", host, json=data, timeout=70)
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


async def pty_stream(
    cmd: list[str],
    stdin_data: str | None = None,
    on_line: Callable[[str], Awaitable[None]] | None = None,
    timeout_s: int = 1800,
) -> tuple[int, list[str]]:
    """
    Spawn *cmd* under a pseudo-terminal so the child never block-buffers
    its stdout.  Read output in chunks and split on ``\\r`` / ``\\n`` so
    sdkmanager-style progress lines (``\\r[===] 34% Downloading...``)
    arrive immediately instead of being held until the 8 KB pipe buffer fills.

    Falls back to a regular pipe on Windows (no PTY support).

    Returns ``(returncode, output_lines)``.
    """
    if platform.system() == "Windows":
        return await _pipe_stream(cmd, stdin_data, on_line, timeout_s)

    import pty as pty_mod

    master_fd, slave_fd = pty_mod.openpty()

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE if stdin_data else asyncio.subprocess.DEVNULL,
        stdout=slave_fd,
        stderr=slave_fd,
    )
    os.close(slave_fd)  # parent only needs the master side

    if stdin_data:
        try:
            proc.stdin.write(stdin_data.encode())
            await proc.stdin.drain()
            proc.stdin.close()
        except Exception:
            pass

    output_lines: list[str] = []
    loop = asyncio.get_event_loop()
    buf = ""

    while True:
        try:
            data: bytes = await asyncio.wait_for(
                loop.run_in_executor(None, os.read, master_fd, 4096),
                timeout=timeout_s,
            )
        except OSError:
            # EIO when slave side closes (child exited)
            break
        except asyncio.TimeoutError:
            break
        if not data:
            break

        buf += data.decode("utf-8", errors="replace")

        # Split on any line-ending (\r\n, \r, or \n)
        parts = re.split(r"\r\n|\r|\n", buf)
        buf = parts[-1]  # keep the incomplete tail
        for part in parts[:-1]:
            line = part.strip()
            if not line:
                continue
            # strip ANSI escape codes the PTY may inject
            line = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", line)
            if not line:
                continue
            output_lines.append(line)
            if on_line:
                await on_line(line)

    # flush any remaining partial line
    remaining = buf.strip()
    if remaining:
        remaining = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", remaining)
        if remaining:
            output_lines.append(remaining)
            if on_line:
                await on_line(remaining)

    try:
        os.close(master_fd)
    except OSError:
        pass

    returncode = await proc.wait()
    return returncode, output_lines


async def _pipe_stream(
    cmd: list[str],
    stdin_data: str | None = None,
    on_line: Callable[[str], Awaitable[None]] | None = None,
    timeout_s: int = 1800,
) -> tuple[int, list[str]]:
    """Fallback for Windows: plain pipe + readline."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE if stdin_data else asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    if stdin_data:
        try:
            proc.stdin.write(stdin_data.encode())
            await proc.stdin.drain()
            proc.stdin.close()
        except Exception:
            pass

    output_lines: list[str] = []
    while True:
        raw = await proc.stdout.readline()
        if not raw:
            break
        line = raw.decode("utf-8", errors="replace").strip()
        if not line:
            continue
        output_lines.append(line)
        if on_line:
            await on_line(line)

    returncode = await proc.wait()
    return returncode, output_lines
